from django.contrib import admin
from .models import Zone, Camera

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'location', 'status', 'created_at']
    list_filter  = ['status', 'zone']