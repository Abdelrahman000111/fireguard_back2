from rest_framework import serializers
from .models import FCMDevice, NotificationPreference


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FCMDevice
        fields = ['id', 'token', 'platform', 'is_active', 'created_at']
        read_only_fields = ['is_active', 'created_at']

    def validate_platform(self, value):
        if value not in ['android', 'ios']:
            raise serializers.ValidationError("Platform must be 'android' or 'ios'.")
        return value

    def validate_token(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("FCM token cannot be empty.")
        return value.strip()


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = NotificationPreference
        fields = [
            'id',
            'fire_alerts',
            'resolved_alerts',
            'false_alarm_alerts',
            'sound_enabled',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']