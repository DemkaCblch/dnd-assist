
from django.contrib.auth import get_user_model, authenticate, logout
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer  # Импортируйте свой сериализатор


# Create your views here.

def login(request):
    return HttpResponse("login")

def register(request):
    return HttpResponse("register")

def profile(request):
    return HttpResponse("profile")

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)  # Устанавливает сессию
            return Response({"detail": "Login successful."}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        logout(request)  # Удаляет сессию
        return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)


def pageNotFound(request, exception):
    return  HttpResponseNotFound('<img src="https://avatars.mds.yandex.net/i?id=6327d4e69260d1c93797d2b806b31aa1_sr-9242319-images-thumbs&n=13"/>')