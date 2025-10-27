import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


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
    predicted_value = models.FloatField()
    spectrum = models.OneToOneField(Spectrum, on_delete=models.CASCADE, related_name='prediction')
    

class Field(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    # Store polygon as list of [lon, lat] points for testing
    boundary = ArrayField(
        base_field=ArrayField(
            base_field=models.FloatField(),
            size=2
        ),
        size=None
    )

    def __str__(self):
        return self.name
    

class FieldHeatmapPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey("Field", on_delete=models.CASCADE, related_name="heatmap_points")
    latitude = models.FloatField()
    longitude = models.FloatField()
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["field", "timestamp"]),
        ]
        

class Run(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    spectrum = models.ForeignKey(
        "Spectrum", null=True, blank=True, on_delete=models.SET_NULL, related_name="runs"
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    predicted_soc = models.FloatField(null=True, blank=True)
    max_depth_mm = models.FloatField(null=True, blank=True)
    max_weight_kg = models.FloatField(null=True, blank=True)
    compaction_pa = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Run {self.id} ({self.timestamp})"


class FieldCompactionHeatmapPoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey("Field", on_delete=models.CASCADE, related_name="compaction_heatmap_points")
    latitude = models.FloatField()
    longitude = models.FloatField()
    value = models.FloatField()  # compaction in Pa
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["field", "timestamp"]),
        ]


class PiCommand(models.Model):
    device_id = models.CharField(max_length=64)
    command = models.CharField(max_length=64)
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_id} - {self.command}"