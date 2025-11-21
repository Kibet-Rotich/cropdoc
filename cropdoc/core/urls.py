from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'crops', CropViewSet)
router.register(r'diseases', CropDiseaseViewSet)
router.register(r'treatments', DiseaseTreatmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get-treatment/', get_treatment_by_disease),
    path('diseases/', get_all_diseases, name='all-diseases'),
    path('user-stats/', user_stats),
    path('sample-images/', get_sample_images),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
