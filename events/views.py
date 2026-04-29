from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FireEvent
from .serializers import (
    FireEventSerializer,
    FireEventCreateSerializer,
    FireEventUpdateSerializer,
)
from notifications.fcm import send_fire_alert_to_all, send_resolved_alert


class FireEventListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]   
        return [IsAuthenticated()]

    def get(self, request):
        events = FireEvent.objects.select_related('camera', 'camera__zone').all()

        event_status = request.query_params.get('status')
        if event_status:
            events = events.filter(status=event_status)

        camera_id = request.query_params.get('camera')
        if camera_id:
            events = events.filter(camera_id=camera_id)

        zone_id = request.query_params.get('zone')
        if zone_id:
            events = events.filter(camera__zone_id=zone_id)

        event_type = request.query_params.get('type')  
        if event_type:
            events = events.filter(event_type=event_type)

        serializer = FireEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FireEventCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()

            fcm_result = send_fire_alert_to_all(event)

            return Response({
                "message": "Event created and notification sent.",
                "event": FireEventSerializer(event).data,
                "fcm": fcm_result
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FireEventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return FireEvent.objects.select_related('camera', 'camera__zone').get(pk=pk)
        except FireEvent.DoesNotExist:
            return None

    def get(self, request, pk):
        event = self.get_object(pk)
        if not event:
            return Response({"error": "Event not found"}, status=404)
        return Response(FireEventSerializer(event).data)

    def patch(self, request, pk):
        event = self.get_object(pk)
        if not event:
            return Response({"error": "Event not found"}, status=404)

        serializer = FireEventUpdateSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(FireEventSerializer(event).data)

        return Response(serializer.errors, status=400)


class ResolveEventView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            event = FireEvent.objects.get(pk=pk)
        except FireEvent.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

        event.status = 'resolved'
        event.resolved_at = timezone.now()
        event.save()

        send_resolved_alert(event)

        return Response({
            "message": "Resolved",
            "event": FireEventSerializer(event).data
        })


class FalseAlarmView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            event = FireEvent.objects.get(pk=pk)
        except FireEvent.DoesNotExist:
            return Response({"error": "Event not found"}, status=404)

        event.status = 'false_alarm'
        event.resolved_at = timezone.now()
        event.save()

        return Response({
            "message": "Marked as false alarm",
            "event": FireEventSerializer(event).data
        })


class ActiveEventView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        event = FireEvent.objects.filter(status='active').order_by('-detected_at').first()

        if not event:
            return Response({"active": False})

        return Response({
            "active": True,
            "event": FireEventSerializer(event).data
        })


class EventStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "total": FireEvent.objects.count(),
            "fire": FireEvent.objects.filter(event_type='fire').count(), 
            "smoke": FireEvent.objects.filter(event_type='smoke').count(),  
            "active": FireEvent.objects.filter(status='active').count(),
            "resolved": FireEvent.objects.filter(status='resolved').count(),
            "false_alarm": FireEvent.objects.filter(status='false_alarm').count(),
        })