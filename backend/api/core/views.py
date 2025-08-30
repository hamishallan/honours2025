import math
import numpy as np
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from shapely.geometry import Polygon, Point, box

from .models import Spectrum, SpectrumDataPoint, Prediction, Field, FieldHeatmapPoint
from .serializers import SpectrumDetailSerializer, PredictionSerializer, FieldSerializer


@api_view(['GET'])
def list_spectra(request):
    """
    Optional query params:
      - near=lon,lat
      - radius_m=number (metres)
    Filters by a bounding box around (lon, lat) with an approximate radius.
    """
    spectra = (
        Spectrum.objects
        .select_related('prediction')
        .prefetch_related('data')
        .order_by('-timestamp')
    )

    near = request.query_params.get("near")
    r_m = request.query_params.get("radius_m")

    if near and r_m:
        try:
            lon0, lat0 = map(float, near.split(","))
            r = float(r_m)

            # Approximate metres per degree.
            # 1 degree latitude ≈ 111,320 m.
            # 1 degree longitude ≈ 111,320 * cos(latitude) m (avoid divide-by-zero at poles).
            m_per_deg_lat = 111_320.0
            m_per_deg_lon = 111_320.0 * max(1e-6, math.cos(math.radians(lat0)))

            dlat = r / m_per_deg_lat
            dlon = r / m_per_deg_lon

            lat_min, lat_max = lat0 - dlat, lat0 + dlat
            lon_min, lon_max = lon0 - dlon, lon0 + dlon

            spectra = spectra.filter(
                Q(latitude__isnull=False) & Q(longitude__isnull=False) &
                Q(latitude__gte=lat_min, latitude__lte=lat_max) &
                Q(longitude__gte=lon_min, longitude__lte=lon_max)
            )
        except (ValueError, TypeError):
            # Bad params → ignore filter
            pass

    serializer = SpectrumDetailSerializer(spectra, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def upload_spectrum(request):
    """
    Accepts either:
      - GeoJSON Point:
          "location": {"type": "Point", "coordinates": [lon, lat]}
      - or floats:
          "longitude": <float>, "latitude": <float>

    Optional:
      - "altitude_m": <float>
      - "accuracy_m": <float>
    """
    wavelengths = request.data.get("wavelengths")
    intensities = request.data.get("intensities")
    device_id = request.data.get("device_id", "unknown")

    if not wavelengths or not intensities or len(wavelengths) != len(intensities):
        return Response({"error": "Invalid spectrum data"}, status=status.HTTP_400_BAD_REQUEST)

    # Parse optional location
    latitude = None
    longitude = None
    location_payload = request.data.get("location")
    lat_in = request.data.get("latitude")
    lon_in = request.data.get("longitude")

    try:
        if isinstance(location_payload, dict) and location_payload.get("type") == "Point":
            coords = location_payload.get("coordinates", [])
            if len(coords) == 2:
                # GeoJSON order is [lon, lat]
                longitude = float(coords[0])
                latitude = float(coords[1])
        elif lat_in is not None and lon_in is not None:
            latitude = float(lat_in)
            longitude = float(lon_in)
    except (ValueError, TypeError):
        latitude = None
        longitude = None

    # Parse optional altitude/accuracy
    def to_float_or_none(v):
        try:
            return float(v) if v not in (None, "") else None
        except (ValueError, TypeError):
            return None

    altitude_m = to_float_or_none(request.data.get("altitude_m"))
    accuracy_m = to_float_or_none(request.data.get("accuracy_m"))

    # Save the Spectrum metadata
    spectrum = Spectrum.objects.create(
        device_id=device_id,
        latitude=latitude,
        longitude=longitude,
        altitude_m=altitude_m,
        accuracy_m=accuracy_m,
    )

    # Prepare data point objects
    data_points = [
        SpectrumDataPoint(spectrum=spectrum, wavelength=w, intensity=i)
        for w, i in zip(wavelengths, intensities)
    ]

    # Bulk insert for speed
    SpectrumDataPoint.objects.bulk_create(data_points)

    return Response({
        "message": "Spectrum uploaded",
        "spectrum_id": str(spectrum.id),
        "points_saved": len(data_points)
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def upload_prediction(request):
    serializer = PredictionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Prediction saved."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def fields_view(request):
    if request.method == 'GET':
        fields = Field.objects.all()
        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Field created", "field": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def fields_geojson(request):
    fields = Field.objects.all()
    features = []

    for f in fields:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [f.boundary]
            },
            "properties": {
                "id": str(f.id),
                "name": f.name,
            }
        })

    return Response({
        "type": "FeatureCollection",
        "features": features
    })
    

def idw_predict(x, y, samples, power=2):
    """
    Inverse Distance Weighting interpolation.
    samples: [(lon, lat, value), ...]
    """
    weights, values = [], []
    for sx, sy, val in samples:
        d = np.sqrt((x - sx)**2 + (y - sy)**2)
        if d == 0:  # exact match
            return val
        w = 1 / (d**power)
        weights.append(w)
        values.append(val * w)
    return sum(values) / sum(weights) if weights else None


@api_view(['GET'])
def field_heatmap(request, field_id):
    """
    Returns a GeoJSON FeatureCollection of small grid cells,
    each coloured by interpolated SOC inside the field polygon.
    """
    try:
        field = Field.objects.get(pk=field_id)
    except Field.DoesNotExist:
        return Response({"error": "Field not found"}, status=404)

    poly = Polygon(field.boundary)

    # Collect all sample points with predictions
    spectra = Spectrum.objects.filter(
        prediction__isnull=False,
        latitude__isnull=False,
        longitude__isnull=False
    )
    samples = [(s.longitude, s.latitude, s.prediction.predicted_value) for s in spectra]

    if not samples:
        return Response({"error": "No prediction data available"}, status=404)

    # Create grid over bounding box
    minx, miny, maxx, maxy = poly.bounds
    cell_size = float(request.query_params.get("cell_size", 0.001))  # degrees (~100m at equator)

    features = []
    points = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + cell_size, y + cell_size)
            # Clip to field polygon
            clipped = cell.intersection(poly)
            if not clipped.is_empty:
                # Interpolate value at cell centroid
                cx, cy = clipped.centroid.x, clipped.centroid.y
                val = idw_predict(cx, cy, samples)
                if val is not None:
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [list(clipped.exterior.coords)]
                        },
                        "properties": {
                            "value": val
                        }
                    })
                    points.append((cy, cx, val))
            y += cell_size
        x += cell_size
    
    if points:
        save_heatmap_points(field, points)

    return Response({
        "type": "FeatureCollection",
        "features": features
    })


def save_heatmap_points(field, points):
    objs = [
        FieldHeatmapPoint(field=field, latitude=lat, longitude=lon, value=val)
        for lat, lon, val in points
    ]
    FieldHeatmapPoint.objects.bulk_create(objs)
    