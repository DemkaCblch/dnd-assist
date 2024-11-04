from django.urls import path

from . import consumers
from .consumers import *

ws_urlpatterns = [
    path('ws/some-url/', RoomConsumer.as_asgi()),
    # Подключение к комнате (каналу)
    path('ws/room/<int:room_id>/', consumers.RoomConsumer.as_asgi()),
    # Канал для получения списка комнат
    path('ws/rooms/', consumers.RoomUpdateConsumer.as_asgi()),
]
