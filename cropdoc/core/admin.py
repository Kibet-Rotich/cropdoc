from django.contrib import admin
from .models import User, Crop, CropDisease, DiseaseTreatment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'role', 'country', 'county', 'consent')
    search_fields = ('name', 'user_id')
    list_filter = ('role', 'country')

admin.site.register(Crop)
admin.site.register(CropDisease)
admin.site.register(DiseaseTreatment)
