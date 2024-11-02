from django.urls import path

from . import consumers
from .consumers import *

ws_urlpatterns = [
    path('ws/some-url/', RoomConsumer.as_asgi()),
    path('ws/room/<str:room_name>/', consumers.RoomConsumer.as_asgi()),
]
