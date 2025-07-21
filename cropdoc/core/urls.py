from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'crops', CropViewSet)
router.register(r'diseases', CropDiseaseViewSet)
router.register(r'treatments', DiseaseTreatmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-treatment/', get_treatment_by_disease),
    path('user-stats/', user_stats),
    path('mock-classify/', mock_classification),
    path('sample-images/', get_sample_images),
]
