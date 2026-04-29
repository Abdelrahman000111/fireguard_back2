from django.urls import path
from .views import (
    ZoneListCreateView,
    ZoneDetailView,
    CameraListCreateView,
    CameraDetailView,
    CameraStatusUpdateView,
    CameraStatsView,
)

urlpatterns = [
    path('stats/', CameraStatsView.as_view(), name='camera-stats'),
    path('zones/', ZoneListCreateView.as_view(), name='zone-list-create'),
    path('zones/<int:pk>/', ZoneDetailView.as_view(), name='zone-detail'),
    path('cameras/', CameraListCreateView.as_view(), name='camera-list-create'),
    path('cameras/<int:pk>/', CameraDetailView.as_view(), name='camera-detail'),
    path('cameras/<int:pk>/status/', CameraStatusUpdateView.as_view(), name='camera-status'),
]