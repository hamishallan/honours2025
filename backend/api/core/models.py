import uuid
from django.db import models


class Spectrum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255)
    latitude   = models.FloatField(null=True, blank=True)
    longitude  = models.FloatField(null=True, blank=True)
    altitude_m = models.FloatField(null=True, blank=True)
    accuracy_m = models.FloatField(null=True, blank=True)
    
class SpectrumDataPoint(models.Model):
    spectrum = models.ForeignKey(Spectrum, related_name='data', on_delete=models.CASCADE)
    wavelength = models.FloatField()
    intensity = models.FloatField()
    
class Prediction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255)
    predicted_value = models.FloatField()
    spectrum = models.OneToOneField(Spectrum, on_delete=models.CASCADE, related_name='prediction')