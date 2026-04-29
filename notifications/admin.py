from django.contrib import admin
from .models import FCMDevice, NotificationPreference

@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'is_active', 'created_at']

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'fire_alerts', 'resolved_alerts', 'sound_enabled']