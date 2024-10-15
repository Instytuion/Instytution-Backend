import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import class_room.routing
from .middleware import WSJWTAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instytution_backend.settings')
django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": WSJWTAuthMiddleware(
        URLRouter(
            class_room.routing.websocket_urlpatterns
        )
    ),
})
