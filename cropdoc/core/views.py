from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import User, Crop, CropDisease, DiseaseTreatment
from .serializers import *

# 1. ViewSets for CRUD
class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

class CropDiseaseViewSet(viewsets.ModelViewSet):
    queryset = CropDisease.objects.all()
    serializer_class = CropDiseaseSerializer

class DiseaseTreatmentViewSet(viewsets.ModelViewSet):
    queryset = DiseaseTreatment.objects.all()
    serializer_class = DiseaseTreatmentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# 2. Get treatment for a disease (by ID or name)
@api_view(['GET'])
def get_treatment_by_disease(request):
    disease_id = request.GET.get('id')
    disease_name = request.GET.get('name')
    
    if disease_id:
        treatments = DiseaseTreatment.objects.filter(disease_id=disease_id)
    elif disease_name:
        try:
            disease = CropDisease.objects.get(disease_name__iexact=disease_name)
            treatments = DiseaseTreatment.objects.filter(disease=disease)
        except CropDisease.DoesNotExist:
            return Response({"error": "Disease not found"}, status=404)
    else:
        return Response({"error": "Provide disease id or name"}, status=400)

    serializer = DiseaseTreatmentSerializer(treatments, many=True)
    return Response(serializer.data)


# 3. User statistics by country and county
@api_view(['GET'])
def user_stats(request):
    by_country = User.objects.values('country').annotate(total=Count('id'))
    by_county = User.objects.values('county').annotate(total=Count('id')).exclude(county=None)
    
    return Response({
        "by_country": by_country,
        "by_county": by_county
    })
