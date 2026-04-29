import firebase_admin
from firebase_admin import messaging
from django.conf import settings


# =========================
# Helpers
# =========================

def _get_event_config(event):
    """
    Returns dynamic config based on event type (fire / smoke)
    """

    event_type = getattr(event, "event_type", "fire")

    if event_type == "smoke":
        return {
            "title": "💨 Smoke Detected!",
            "type": "smoke_alert",
        }

    # default = fire
    return {
        "title": "🔥 Fire Detected!",
        "type": "fire_alert",
    }


def _handle_failed_tokens(tokens, response):
    from notifications.models import FCMDevice

    failed_tokens = [
        tokens[i]
        for i, resp in enumerate(response.responses)
        if not resp.success
    ]

    if failed_tokens:
        FCMDevice.objects.filter(token__in=failed_tokens).update(is_active=False)


# =========================
# Fire / Smoke Alert
# =========================

def send_fire_alert_to_all(event):
    """
    Send FIRE or SMOKE alert to all eligible users
    """

    try:
        from notifications.models import FCMDevice, NotificationPreference

        config = _get_event_config(event)

        opted_in_users = NotificationPreference.objects.filter(
            fire_alerts=True
        ).values_list('user_id', flat=True)

        tokens = list(
            FCMDevice.objects.filter(
                is_active=True,
                user_id__in=opted_in_users
            ).values_list('token', flat=True)
        )

        if not tokens:
            return {"status": "skipped", "reason": "No eligible devices found."}

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title=config["title"],
                body=(
                    f"{event.camera.location} — "
                    f"{event.camera.zone.name} — "
                    f"{event.ai_confidence:.1f}% confidence"
                ),
            ),
            data={
                "type": config["type"],
                "event_id": str(event.id),
                "camera_id": str(event.camera.id),
                "camera_name": event.camera.name,
                "location": event.camera.location,
                "zone": event.camera.zone.name,
                "event_type": event.event_type,
                "ai_confidence": str(event.ai_confidence),
                "detected_at": event.detected_at.isoformat(),
            },
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    channel_id='alerts',
                ),
            ),
            apns=messaging.APNSConfig(
                headers={'apns-priority': '10'},
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                        content_available=True,
                    ),
                ),
            ),
        )

        response = messaging.send_each_for_multicast(message)
        _handle_failed_tokens(tokens, response)

        return {
            "status": "sent",
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# =========================
# Resolved Alert
# =========================

def send_resolved_alert(event):
    try:
        from notifications.models import FCMDevice, NotificationPreference

        opted_in_users = NotificationPreference.objects.filter(
            resolved_alerts=True
        ).values_list('user_id', flat=True)

        tokens = list(
            FCMDevice.objects.filter(
                is_active=True,
                user_id__in=opted_in_users
            ).values_list('token', flat=True)
        )

        if not tokens:
            return {"status": "skipped"}

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(
                title="✅ Event Resolved",
                body=f"{event.camera.location} has been resolved.",
            ),
            data={
                "type": "event_resolved",
                "event_id": str(event.id),
                "event_type": event.event_type,
            },
        )

        response = messaging.send_each_for_multicast(message)
        _handle_failed_tokens(tokens, response)

        return {
            "status": "sent",
            "success_count": response.success_count,
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}


# =========================
# Test Push
# =========================

def send_test_push(token):
    try:
        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title="FireGuard Test",
                body="Push notifications working correctly.",
            ),
            data={"type": "test"},
        )
        message_id = messaging.send(message)
        return {"status": "sent", "message_id": message_id}

    except Exception as e:
        return {"status": "error", "detail": str(e)}