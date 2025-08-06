from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Spectrum, SpectrumDataPoint, Prediction
from .serializers import SpectrumDetailSerializer, PredictionSerializer


@api_view(['GET'])
def list_spectra(request):
    spectra = Spectrum.objects.all().order_by('-timestamp')  # most recent first
    serializer = SpectrumDetailSerializer(spectra, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def upload_spectrum(request):
    wavelengths = request.data.get("wavelengths")
    intensities = request.data.get("intensities")
    device_id = request.data.get("device_id", "unknown")

    if not wavelengths or not intensities or len(wavelengths) != len(intensities):
        return Response({"error": "Invalid spectrum data"}, status=status.HTTP_400_BAD_REQUEST)

    # Save the Spectrum metadata
    spectrum = Spectrum.objects.create(device_id=device_id)

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
