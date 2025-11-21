# core/views.py

# ─── Standard Library Imports ────────────────────────────────────────────────
import os

# ─── Django Imports ───────────────────────────────────────────────────────────
from django.conf import settings
from django.db.models import Count

# ─── DRF Imports ──────────────────────────────────────────────────────────────
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

# ─── Local Imports ────────────────────────────────────────────────────────────
from .models import User, Crop, CropDisease, DiseaseTreatment
from .serializers import (
    UserSerializer,
    CropSerializer,
    CropDiseaseSerializer,
    DiseaseTreatmentSerializer,
)



# ─────────────────────────────────────────────────────────────────────────────
# Utility Function: Get Treatments for a Disease
# ─────────────────────────────────────────────────────────────────────────────
def get_treatments_for_disease(disease_id=None, disease_name=None):
    """
    Retrieve treatment recommendations for a given disease.
    Accepts either `disease_id` or `disease_name`.
    """
    if disease_id:
        treatments = DiseaseTreatment.objects.filter(disease_id=disease_id)
    elif disease_name:
        try:
            disease = CropDisease.objects.get(disease_name__iexact=disease_name)
            treatments = DiseaseTreatment.objects.filter(disease=disease)
        except CropDisease.DoesNotExist:
            return None, "Disease not found"
    else:
        return None, "Provide disease ID or name"

    serializer = DiseaseTreatmentSerializer(treatments, many=True)
    return serializer.data, None


# ─────────────────────────────────────────────────────────────────────────────
# ViewSets (CRUD Endpoints)
# ─────────────────────────────────────────────────────────────────────────────
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer


class CropDiseaseViewSet(viewsets.ModelViewSet):
    queryset = CropDisease.objects.all()
    serializer_class = CropDiseaseSerializer


class DiseaseTreatmentViewSet(viewsets.ModelViewSet):
    queryset = DiseaseTreatment.objects.all()
    serializer_class = DiseaseTreatmentSerializer


# ─────────────────────────────────────────────────────────────────────────────
# API: Get Treatment by Disease
# ─────────────────────────────────────────────────────────────────────────────
@api_view(["GET"])
def get_treatment_by_disease(request):
    """
    Retrieve treatment recommendations for a specific crop disease.
    Supports filtering by `id` or `name` query parameter.
    """
    disease_id = request.GET.get("id")
    disease_name = request.GET.get("name")

    data, error = get_treatments_for_disease(disease_id, disease_name)
    if error:
        return Response({"error": error}, status=400)

    return Response(data)

# ─────────────────────────────────────────────────────────────────────────────
# API: Get All Diseases
# ─────────────────────────────────────────────────────────────────────────────
@api_view(["GET"])
def get_all_diseases(request):
    """
    Retrieve a list of all CropDisease objects with their ID, name, 
    characteristics, and associated crop name.
    """
    # Use select_related to fetch the Crop object in the same query 
    # to avoid the N+1 query problem.
    diseases = CropDisease.objects.select_related('crop').all()
    
    # We will use the existing CropDiseaseSerializer, which should include all fields.
    serializer = CropDiseaseSerializer(diseases, many=True)
    
    return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# API: User Statistics
# ─────────────────────────────────────────────────────────────────────────────
@api_view(["GET"])
def user_stats(request):
    """
    Returns counts of users grouped by country and county.
    """
    by_country = User.objects.values("country").annotate(total=Count("id"))
    by_county = (
        User.objects.values("county")
        .annotate(total=Count("id"))
        .exclude(county=None)
    )

    return Response({
        "by_country": by_country,
        "by_county": by_county,
    })


# ─────────────────────────────────────────────────────────────────────────────
# API: Get Sample Images
# ─────────────────────────────────────────────────────────────────────────────
from urllib.parse import quote

@api_view(["GET"])
def get_sample_images(request):
    """
    Returns a list of sample images from `media/sample_images/`.
    Each entry contains the image name and its encoded URL.
    """
    sample_folder = os.path.join(settings.MEDIA_ROOT, "sample_images")
    if not os.path.exists(sample_folder):
        return Response({"images": []})

    media_url_prefix = request.build_absolute_uri(settings.MEDIA_URL + "sample_images/")

    images = []
    for file_name in os.listdir(sample_folder):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            encoded_name = quote(file_name)
            images.append({
                "name": file_name,
                "url": media_url_prefix + encoded_name,
            })

    return Response({"images": images})

