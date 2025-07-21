from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from .models import User, Crop, CropDisease, DiseaseTreatment
from .serializers import *

from .models import DiseaseTreatment, CropDisease
from .serializers import DiseaseTreatmentSerializer

def get_treatments_for_disease(disease_id=None, disease_name=None):
    if disease_id:
        treatments = DiseaseTreatment.objects.filter(disease_id=disease_id)
    elif disease_name:
        try:
            disease = CropDisease.objects.get(disease_name__iexact=disease_name)
            treatments = DiseaseTreatment.objects.filter(disease=disease)
        except CropDisease.DoesNotExist:
            return None, "Disease not found"
    else:
        return None, "Provide disease id or name"

    serializer = DiseaseTreatmentSerializer(treatments, many=True)
    return serializer.data, None


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

    data, error = get_treatments_for_disease(disease_id, disease_name)

    if error:
        return Response({"error": error}, status=400)

    return Response(data)



# 3. User statistics by country and county
@api_view(['GET'])
def user_stats(request):
    by_country = User.objects.values('country').annotate(total=Count('id'))
    by_county = User.objects.values('county').annotate(total=Count('id')).exclude(county=None)
    
    return Response({
        "by_country": by_country,
        "by_county": by_county
    })


import os
import random
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import CropDisease
from .views import get_treatment_by_disease  # Assuming same file, otherwise import properly

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def mock_classification(request):
    image = request.FILES.get('image', None)

    saved_image_path = None

    if image:
        folder = os.path.join(settings.MEDIA_ROOT, 'classified_images')
        os.makedirs(folder, exist_ok=True)

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.name}"
        filepath = os.path.join(folder, filename)

        with open(filepath, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        saved_image_path = os.path.join('classified_images', filename)

    # 33% chance it's healthy
    is_healthy = random.choice([True, False, False])

    if is_healthy:
        return Response({
            "result": "Healthy",
            "confidence": round(random.uniform(0.9, 1.0), 2),
            "saved_image": saved_image_path,
            "recommendation": None
        })

    # Pick a random disease
    diseases = CropDisease.objects.all()
    if not diseases.exists():
        return Response({"error": "No diseases in DB"}, status=404)

    disease = random.choice(diseases)

    # Create a dummy GET request to simulate calling the original function
    class DummyRequest:
        GET = {'id': str(disease.disease_id)}

    treatment_data, error = get_treatments_for_disease(disease_id=disease.disease_id)


    return Response({
        "result": disease.disease_name,
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "recommendation": treatment_data,  # List of treatments
        "saved_image": saved_image_path
    })


import os
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_sample_images(request):
    sample_folder = os.path.join(settings.MEDIA_ROOT, 'sample_images')
    media_url_prefix = request.build_absolute_uri(settings.MEDIA_URL + 'sample_images/')

    if not os.path.exists(sample_folder):
        return Response({"images": []})

    image_urls = []
    for file_name in os.listdir(sample_folder):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            full_url = media_url_prefix + file_name
            image_urls.append(full_url)

    return Response({"images": image_urls})
