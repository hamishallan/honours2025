from rest_framework import serializers
from .models import Spectrum, SpectrumDataPoint, Prediction

class SpectrumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spectrum
        fields = ['id', 'timestamp', 'device_id']


class SpectrumDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpectrumDataPoint
        fields = ['wavelength', 'intensity']


class SpectrumDetailSerializer(serializers.ModelSerializer):
    data = SpectrumDataPointSerializer(many=True, read_only=True)

    class Meta:
        model = Spectrum
        fields = ['id', 'timestamp', 'device_id', 'data']
        

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['device_id', 'predicted_value', 'spectrum']