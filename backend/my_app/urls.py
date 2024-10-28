from django.urls import path, include, re_path

from . import consumers
from .views import *
from .consumers import *
from djoser import views as djoser_views


urlpatterns = [
    #Для регистрирования пользователя
    path('api/auth/', include('djoser.urls')),
    #Для захода в пользователя
    re_path('api/auth/', include('djoser.urls.authtoken')),

    path('api/create-character/', CreateCharacterAPIView.as_view(), name='create-character'),
]
