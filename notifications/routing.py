# notifications/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # The WebSocket will connect here, using user ID
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
