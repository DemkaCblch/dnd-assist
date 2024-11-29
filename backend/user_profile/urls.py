from django.urls import path, include, re_path

from .views import *

urlpatterns = [
    # Регистрция (users/)
    path('api/auth/', include('djoser.urls')),

    # Логин (login/token/)
    re_path('api/auth/', include('djoser.urls.authtoken')),

    # Личный кабинет
    #path('api/profile/', CreateCharacterAPIView.as_view(), name='user-profile'),

    # Создание персонажа
    path('api/create-character/', CreateCharacterAPIView.as_view(), name='create-character'),

    # Получение персонажа
    # path('api/get-character/', GetCharacterAPIView.as_view(), name='get-character'),
]
