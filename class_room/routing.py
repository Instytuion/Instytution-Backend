from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path('class-room/<str:batch_name>/', ClassRoomConsumer.as_asgi() , name='ws_class_room'),
]