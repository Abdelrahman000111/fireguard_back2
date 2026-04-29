from django.contrib import admin
from .models import FireEvent

@admin.register(FireEvent)
class FireEventAdmin(admin.ModelAdmin):
    list_display  = ['id', 'camera', 'status', 'ai_confidence', 'detected_at']
    list_filter   = ['status']
    ordering      = ['-detected_at']