from django.urls import path

from .views import *

urlpatterns = [
    # Получение списка комнат
    path('api/rooms/', GetRoomsAPIView.as_view(), name='get-rooms'),

    # Создание комнаты
    path('api/create-room/', CreateRoomAPIView.as_view(), name='create-room'),

    # Подключение к комнате
    path('api/connect-room/<int:room_id>/', JoinRoomAPIView.as_view(), name='join-room'),

    # Закрытие комнаты
    path('api/delete-room/<int:room_id>/', DeleteRoomAPIView.as_view(), name='close-room'),

    path('api/get-info-room/<int:room_id>/', GetRoomInfoAPIView.as_view(), name='get-info-room'),

    path('api/rooms/<int:room_id>/is_master/', GetAmIMasterAPIView.as_view(), name='is_master'),
]
