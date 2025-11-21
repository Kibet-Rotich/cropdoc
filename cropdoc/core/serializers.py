from rest_framework import serializers
from .models import User, Crop, CropDisease, DiseaseTreatment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = '__all__'


class CropDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropDisease
        fields = '__all__'


class DiseaseTreatmentSerializer(serializers.ModelSerializer):
    disease_name = serializers.CharField(source="disease.disease_name", read_only=True)
    symptoms = serializers.CharField(source="disease.symptoms", read_only=True)
    prevention = serializers.CharField(source="disease.prevention", read_only=True)

    class Meta:
        model = DiseaseTreatment
        fields = [
            "drug_id",
            "drug_name",
            "drug_administration_instructions",
            "disease",       # ID
            "crop",
            "disease_name",  # New
            "symptoms",      # New
            "prevention",    # New
        ]

