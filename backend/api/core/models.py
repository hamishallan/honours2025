import uuid
from django.db import models

class Spectrum(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=100)

class SpectrumDataPoint(models.Model):
    spectrum = models.ForeignKey(Spectrum, related_name='data', on_delete=models.CASCADE)
    wavelength = models.FloatField()
    intensity = models.FloatField()