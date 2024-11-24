from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from my_app.models import Room, Character, PlayerInRoom
from my_app.serializers import CharacterSerializer, RoomSerializer, JoinRoomSerializer


def pageNotFound(request, exception):
    return HttpResponseNotFound(
        '<img src="https://avatars.mds.yandex.net/i?id=6327d4e69260d1c93797d2b806b31aa1_sr-9242319-images-thumbs&n=13'
        '"/>')


class CreateCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных пользователей

    def post(self, request, *args, **kwargs):
        serializer = CharacterSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            character = serializer.save()  # Сохраняем персонажа
            return Response({
                'message': 'Character created successfully',
                'character': CharacterSerializer(character).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            room = serializer.save()  # Создаем новую комнату
            print(f"Room created successfully: {room.name} (ID: {room.id})")

            # Получаем channel_layer
            channel_layer = get_channel_layer()

            # Подготовка данных для отправки в WebSocket
            room_data = {
                'id': room.id,
                'name': room.name,
                'status': room.room_status
            }
            print(f"Sending to channel group 'chat_{room.id}' with data: {room_data}")

            try:
                # Отправляем обновление в группу комнаты
                async_to_sync(channel_layer.group_send)(
                    f'chat_{room.id}',  # Динамическая группа для конкретной комнаты
                    {
                        'type': 'new_room_created',
                        'room': room_data
                    }
                )
                print("Message sent to WebSocket group successfully.")
            except Exception as e:
                print(f"Error sending message to WebSocket group: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Извлекаем токен пользователя из заголовков запроса
        token_key = request.headers.get('Authorization')
        if token_key:
            token = Token.objects.get(key=token_key.split()[1])  # Извлекаем токен из 'Token <token>'
            user = token.user
        else:
            raise PermissionDenied("Token is missing or invalid.")

        # Проверяем, существует ли комната с данным ID
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"detail": "Room not found"}, status=404)

        # Проверяем, что пользователь не является мастером комнаты
        if room.master_token == str(token):
            return Response({"detail": "You are the master of the room and cannot join as a player."}, status=400)

        # Проверка, есть ли уже пользователь в комнате
        if PlayerInRoom.objects.filter(user_token=str(token), room=room).exists():
            return Response({"detail": "You are already in this room."}, status=400)

        # Извлекаем персонажа, за которого играет пользователь
        character_id = request.data.get('character_id')
        try:
            character = Character.objects.get(id=character_id, user_token=str(token))
        except Character.DoesNotExist:
            return Response({"detail": "Character not found or does not belong to the user."}, status=400)

        # Создаем связь игрока с комнатой и персонажем
        PlayerInRoom.objects.create(
            user_token=token,  # Связываем с токеном пользователя
            room=room,
            character=character
        )
        return Response(status=200)



class CloseRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Извлекаем токен пользователя из заголовков запроса
        token_key = request.headers.get('Authorization')
        if token_key:
            token = Token.objects.get(key=token_key.split()[1])  # Извлекаем токен из 'Token <token>'
            user = token.user
        else:
            raise PermissionDenied("Token is missing or invalid.")

        try:
            room = Room.objects.get(id=room_id, master=user)  # Используем пользователя, полученного через токен

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
