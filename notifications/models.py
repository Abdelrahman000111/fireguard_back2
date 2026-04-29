from django.db import models
from django.contrib.auth.models import User


class FCMDevice(models.Model):

    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios',     'iOS'),
    ]

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_devices')
    token       = models.TextField(unique=True)
    platform    = models.CharField(max_length=10, choices=PLATFORM_CHOICES, default='android')
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.platform} device"


class NotificationPreference(models.Model):
    user                    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_prefs')
    fire_alerts             = models.BooleanField(default=True)
    resolved_alerts         = models.BooleanField(default=True)
    false_alarm_alerts      = models.BooleanField(default=False)
    sound_enabled           = models.BooleanField(default=True)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Notification Prefs"