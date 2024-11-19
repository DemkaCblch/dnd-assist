from django.urls import path, include, re_path

from . import consumers
from .views import *
from .consumers import *
from djoser import views as djoser_views

urlpatterns = [
    # Для регистрирования пользователя
    path('api/auth/', include('djoser.urls')),
    # Для захода в пользователя
    re_path('api/auth/', include('djoser.urls.authtoken')),

    # Личный кабинет - реализовать (Возвращает данные о профиле)
    path('api/profile/', CreateCharacterAPIView.as_view(), name='create-character'),

    # Создание персонажа
    path('api/create-character/', CreateCharacterAPIView.as_view(), name='create-character'),

    # Создание комнаты
    path('api/create-room/', CreateRoomAPIView.as_view(), name='create-room'),

    # Подключение к комнате - реализовать (Возвращает, можно ли подключиться и изменяет статус игрока)
    path('api/connect-room/<int:room_id>/', CreateRoomAPIView.as_view(), name='create-room'),

    # Закрытие комнаты
    path('api/close-room/<int:room_id>/', CloseRoomAPIView.as_view(), name='close-room'),
]
