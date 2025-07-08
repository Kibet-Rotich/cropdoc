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
    class Meta:
        model = DiseaseTreatment
        fields = '__all__'
