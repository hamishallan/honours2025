from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, unique=True, null=True)
    age = models.IntegerField(null=True)

    class Meta:
        db_table = "users"  # Map to the existing PostgreSQL table
