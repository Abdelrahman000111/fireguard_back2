from django.urls import path
from .views import (
    FireEventListCreateView,
    FireEventDetailView,
    ResolveEventView,
    FalseAlarmView,
    ActiveEventView,
    EventStatsView,
)

urlpatterns = [
    path('active/', ActiveEventView.as_view(), name='event-active'),
    path('stats/', EventStatsView.as_view(), name='event-stats'),
    path('', FireEventListCreateView.as_view(), name='event-list-create'),
    path('<int:pk>/', FireEventDetailView.as_view(), name='event-detail'),
    path('<int:pk>/resolve/', ResolveEventView.as_view(), name='event-resolve'),
    path('<int:pk>/false-alarm/', FalseAlarmView.as_view(), name='event-false-alarm'),
]