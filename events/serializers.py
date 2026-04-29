from rest_framework import serializers
from .models import FireEvent
from cameras.serializers import CameraSerializer


class FireEventSerializer(serializers.ModelSerializer):
    camera_detail = CameraSerializer(source='camera', read_only=True)
    zone_name     = serializers.CharField(source='camera.zone.name', read_only=True)
    zone_id       = serializers.IntegerField(source='camera.zone.id', read_only=True)

    class Meta:
        model  = FireEvent
        fields = [
            'id',
            'camera',
            'camera_detail',
            'zone_name',
            'zone_id',
            'event_type', 
            'status',
            'ai_confidence',
            'snapshot',
            'notes',
            'detected_at',
            'resolved_at',
        ]
        read_only_fields = ['detected_at', 'resolved_at', 'status']


class FireEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FireEvent
        fields = ['camera', 'event_type', 'ai_confidence', 'snapshot', 'notes']

    def validate_ai_confidence(self, value):
        if not (0.0 <= value <= 100.0):
            raise serializers.ValidationError("AI confidence must be between 0 and 100.")
        return value

    def validate_camera(self, value):
        if value.status == 'offline':
            raise serializers.ValidationError("Cannot create an event for an offline camera.")
        return value


class FireEventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FireEvent
        fields = ['notes']