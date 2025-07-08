from django.contrib import admin
from .models import User, Crop, CropDisease, DiseaseTreatment

admin.site.register(User)
admin.site.register(Crop)
admin.site.register(CropDisease)
admin.site.register(DiseaseTreatment)
