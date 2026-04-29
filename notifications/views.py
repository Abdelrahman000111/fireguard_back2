from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FCMDevice, NotificationPreference
from .serializers import FCMDeviceSerializer, NotificationPreferenceSerializer
from .fcm import send_test_push


class RegisterDeviceView(APIView):
    """
    POST /api/notifications/register-device/
    Flutter app calls this after login with the FCM token.
    If the token already exists it is re-activated and
    re-assigned to the current user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token    = request.data.get('token', '').strip()
        platform = request.data.get('platform', 'android')

        if not token:
            return Response(
                {"error": "FCM token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Upsert — update if token exists, create if not
        device, created = FCMDevice.objects.update_or_create(
            token=token,
            defaults={
                'user':      request.user,
                'platform':  platform,
                'is_active': True,
            }
        )

        serializer = FCMDeviceSerializer(device)
        return Response({
            "message": "Device registered." if created else "Device updated.",
            "device":  serializer.data,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class UnregisterDeviceView(APIView):
    """
    DELETE /api/notifications/unregister-device/
    Flutter app calls this on logout to stop receiving push notifications.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        token = request.data.get('token', '').strip()

        if not token:
            return Response(
                {"error": "FCM token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = FCMDevice.objects.filter(
            user=request.user,
            token=token,
        ).delete()

        if deleted_count == 0:
            return Response(
                {"error": "Token not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Device unregistered successfully."},
            status=status.HTTP_200_OK
        )


class NotificationPreferenceView(APIView):
    """
    GET   /api/notifications/preferences/ — get current prefs
    PATCH /api/notifications/preferences/ — update prefs
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(prefs)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(
            prefs,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Preferences updated.",
                "prefs":   serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestPushView(APIView):
    """
    POST /api/notifications/test-push/
    Development endpoint — sends a test push to a specific token.
    Remove or restrict to admin only before going to production.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token', '').strip()

        if not token:
            # Use the user's own most recent token if none provided
            device = FCMDevice.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-created_at').first()

            if not device:
                return Response(
                    {"error": "No active device token found. Provide a token or register a device first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = device.token

        result = send_test_push(token)
        return Response(result, status=status.HTTP_200_OK)