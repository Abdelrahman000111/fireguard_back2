from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Zone, Camera
from .serializers import ZoneSerializer, CameraSerializer, CameraStatusSerializer


# =============================
# Custom Permission
# =============================
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ─── Zone Views ───────────────────────────────────────────────

class ZoneListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        zones = Zone.objects.annotate(camera_count=Count('cameras')).order_by('-created_at')
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ZoneDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Zone.objects.get(pk=pk)
        except Zone.DoesNotExist:
            return None

    def get(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response({"error": "Zone not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ZoneSerializer(zone)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response({"error": "Zone not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ZoneSerializer(zone, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response({"error": "Zone not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ZoneSerializer(zone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        zone = self.get_object(pk)
        if not zone:
            return Response({"error": "Zone not found."}, status=status.HTTP_404_NOT_FOUND)
        zone.delete()
        return Response({"message": "Zone deleted."}, status=status.HTTP_204_NO_CONTENT)


# ─── Camera Views ─────────────────────────────────────────────

class CameraListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        cameras = Camera.objects.select_related('zone').order_by('-created_at')

        zone_id = request.query_params.get('zone')
        if zone_id:
            cameras = cameras.filter(zone_id=zone_id)

        cam_status = request.query_params.get('status')
        if cam_status:
            cameras = cameras.filter(status=cam_status)

        serializer = CameraSerializer(cameras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CameraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CameraDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return Camera.objects.select_related('zone').get(pk=pk)
        except Camera.DoesNotExist:
            return None

    def get(self, request, pk):
        camera = self.get_object(pk)
        if not camera:
            return Response({"error": "Camera not found."}, status=404)
        return Response(CameraSerializer(camera).data)

    def put(self, request, pk):
        camera = self.get_object(pk)
        if not camera:
            return Response({"error": "Camera not found."}, status=404)
        serializer = CameraSerializer(camera, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request, pk):
        camera = self.get_object(pk)
        if not camera:
            return Response({"error": "Camera not found."}, status=404)
        serializer = CameraSerializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        camera = self.get_object(pk)
        if not camera:
            return Response({"error": "Camera not found."}, status=404)
        camera.delete()
        return Response({"message": "Camera deleted."}, status=204)


class CameraStatusUpdateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def patch(self, request, pk):
        try:
            camera = Camera.objects.get(pk=pk)
        except Camera.DoesNotExist:
            return Response({"error": "Camera not found."}, status=404)

        serializer = CameraStatusSerializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": f"Camera status updated to '{camera.status}'.",
                "id": camera.id,
                "status": camera.status,
            })
        return Response(serializer.errors, status=400)


class CameraStatsView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        total_units = Camera.objects.count()
        online_now  = Camera.objects.filter(status='online').count()

        return Response({
            "total_units": total_units,
            "online_now": online_now,
            "offline": total_units - online_now,
        })