from django.urls import path
from .views import *
from .consumers import GameConsumer

websocket_urlpatterns = [
    path('ws/game/<str:room_name>/', GameConsumer.as_asgi()),  # Путь для WebSocket
]

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
]
