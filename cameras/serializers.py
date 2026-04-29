from rest_framework import serializers
from .models import Zone, Camera


class ZoneSerializer(serializers.ModelSerializer):
    camera_count = serializers.IntegerField(read_only=True)  

    class Meta:
        model  = Zone
        fields = ['id', 'name', 'description', 'camera_count', 'created_at']


class CameraSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model  = Camera
        fields = [
            'id', 'name', 'location', 'zone', 'zone_name',
            'stream_url', 'thumbnail', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CameraStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Camera
        fields = ['id', 'status']

    def validate_status(self, value):
        if value not in ['online', 'offline']:
            raise serializers.ValidationError("Status must be 'online' or 'offline'.")
        return value