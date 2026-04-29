from django.urls import path
from .views import (
    RegisterDeviceView,
    UnregisterDeviceView,
    NotificationPreferenceView,
    TestPushView,
)

urlpatterns = [
    path('register-device/',   RegisterDeviceView.as_view(),          name='register-device'),
    path('unregister-device/', UnregisterDeviceView.as_view(),        name='unregister-device'),
    path('preferences/',       NotificationPreferenceView.as_view(),  name='notification-prefs'),
    path('test-push/',         TestPushView.as_view(),                name='test-push'),
]