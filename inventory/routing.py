from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # Ye path browser ke WebSocket URL se match karna chahiye
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]