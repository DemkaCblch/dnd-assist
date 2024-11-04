from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from my_app.consumers import RoomConsumer, RoomUpdateConsumer
from my_app.models import Room
from my_app.serializers import CharacterSerializer, RoomSerializer


def pageNotFound(request, exception):
    return HttpResponseNotFound(
        '<img src="https://avatars.mds.yandex.net/i?id=6327d4e69260d1c93797d2b806b31aa1_sr-9242319-images-thumbs&n=13'
        '"/>')


class CreateCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CharacterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Обеспечьте, чтобы пользователь был аутентифицирован

    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()  # Сохраняем новую комнату

            # Получаем список всех комнат
            rooms = [
                {'id': room.id, 'name': room.name, 'status': room.room_status}
                for room in Room.objects.all()
            ]

            channel_layer = get_channel_layer()

            # Отправка обновления всем подключенным пользователям
            async_to_sync(channel_layer.group_send)(
                'room_updates',  # Название группы
                {
                    'type': 'update_rooms',
                    'rooms': rooms
                }
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id, master=request.user)

            # Проверка, закрыта ли комната уже
            if room.room_status == 'Closed':
                return Response({'error': 'Room is already closed.'}, status=status.HTTP_400_BAD_REQUEST)

            # Обновляем статус комнаты
            room.room_status = 'Closed'
            room.save()

            # Получаем список всех комнат
            rooms = [
                {'id': r.id, 'name': r.name, 'status': r.room_status}
                for r in Room.objects.all()
            ]

            channel_layer = get_channel_layer()

            # Отправка обновления всем подключенным пользователям
            async_to_sync(channel_layer.group_send)(
                'room_updates',  # Название группы
                {
                    'type': 'update_rooms',
                    'rooms': rooms
                }
            )

            return Response({'message': 'Room closed successfully.'}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)