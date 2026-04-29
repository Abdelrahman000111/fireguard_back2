from django.db import models
from cameras.models import Camera


class FireEvent(models.Model):

    STATUS_CHOICES = [
        ('active',       'Active'),
        ('resolved',     'Resolved'),
        ('false_alarm',  'False Alarm'),
    ]

    EVENT_TYPE_CHOICES = [
        ('fire',  'Fire'),
        ('smoke', 'Smoke'),
    ]

    camera        = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='events')
    event_type    = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES)
    status        = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    ai_confidence = models.FloatField()
    snapshot      = models.ImageField(upload_to='snapshots/', blank=True, null=True)
    notes         = models.TextField(blank=True, null=True)
    detected_at   = models.DateTimeField(auto_now_add=True)
    resolved_at   = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.event_type.upper()} — {self.camera.name} [{self.status}]"