import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from inventory.routing import websocket_urlpatterns # Ab ye kaam karega

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yogesh_inventory.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})