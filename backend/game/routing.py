from django.urls import path
from game import consumers

ws_urlpatterns = [
    # Подключение к комнате (каналу)
    path('ws/room/<int:room_id>/', consumers.RoomConsumer.as_asgi()),

]
