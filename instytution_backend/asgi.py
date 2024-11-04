import os
import django



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instytution_backend.settings')
django.setup() # called django setup before any model access

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import class_room.routing
from .middleware import WSJWTAuthMiddleware

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": WSJWTAuthMiddleware(
        URLRouter(
            class_room.routing.websocket_urlpatterns
        )
    ),
})
