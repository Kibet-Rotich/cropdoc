import uuid
from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('extension_officer', 'Extension Officer'),
        ('researcher', 'Researcher'),
    ]
    COUNTRY_CHOICES = [
        ('Kenya', 'Kenya'),
        ('Other', 'Other'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=20, choices=COUNTRY_CHOICES)
    county = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    consent = models.BooleanField()

    def __str__(self):
        return f"{self.name} ({self.role})"



class Crop(models.Model):
    crop_id = models.AutoField(primary_key=True)
    crop_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.crop_name


class CropDisease(models.Model):
    disease_id = models.AutoField(primary_key=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='diseases')
    disease_name = models.CharField(max_length=100)
    symptoms = models.TextField(null=True, blank=True)
    prevention = models.TextField(null=True, blank=True)


class DiseaseTreatment(models.Model):
    drug_id = models.AutoField(primary_key=True)
    disease = models.ForeignKey(CropDisease, on_delete=models.CASCADE, related_name='treatments')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='treatments')
    drug_name = models.CharField(max_length=100)
    drug_administration_instructions = models.TextField()

    def __str__(self):
        return f"{self.drug_name} for {self.disease.disease_name}"
