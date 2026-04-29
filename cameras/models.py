from django.db import models


class Zone(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Camera(models.Model):

    STATUS_CHOICES = [
        ('online',  'Online'),
        ('offline', 'Offline'),
    ]

    zone        = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='cameras')
    name        = models.CharField(max_length=100)
    location    = models.CharField(max_length=200)      
    stream_url  = models.URLField(blank=True, null=True)    
    thumbnail   = models.ImageField(upload_to='cameras/', blank=True, null=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='online')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.zone.name})"