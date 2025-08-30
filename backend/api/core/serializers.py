from rest_framework import serializers
from .models import Spectrum, SpectrumDataPoint, Prediction, Field


def _to_geojson_point(obj):
    lat = getattr(obj, "latitude", None)
    lon = getattr(obj, "longitude", None)
    if lat is None or lon is None:
        return None
    return {"type": "Point", "coordinates": [lon, lat]}


class SpectrumSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Spectrum
        fields = [
            "id",
            "timestamp",
            "device_id",
            "location",
            "altitude_m",
            "accuracy_m",
        ]

    def get_location(self, obj):
        return _to_geojson_point(obj)


class SpectrumDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpectrumDataPoint
        fields = ["wavelength", "intensity"]


class SpectrumDetailSerializer(serializers.ModelSerializer):
    data = SpectrumDataPointSerializer(many=True, read_only=True)
    predicted_value = serializers.FloatField(
        source="prediction.predicted_value", read_only=True
    )
    location = serializers.SerializerMethodField()

    class Meta:
        model = Spectrum
        fields = [
            "id",
            "timestamp",
            "device_id",
            "data",
            "predicted_value",
            "location",
            "altitude_m",
            "accuracy_m",
        ]

    def get_location(self, obj):
        return _to_geojson_point(obj)


class PredictionSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source="spectrum.device_id", read_only=True)
    
    class Meta:
        model = Prediction
        fields = ["device_id", "predicted_value", "spectrum"]


class FieldSerializer(serializers.ModelSerializer):
    geojson = serializers.SerializerMethodField()

    class Meta:
        model = Field
        fields = ["id", "name", "boundary", "geojson"]

    def get_geojson(self, obj):
        return {
            "type": "Polygon",
            "coordinates": [obj.boundary]  # wrap in list per GeoJSON spec
        }
