from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from room.models import Room, PlayerInRoom
from room.serializers import GetRoomSerializer, CreateRoomSerializer, JoinRoomSerializer
from user_profile.models import Character


class GetRoomsAPIView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = GetRoomSerializer


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateRoomSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            room = serializer.save()
            print(f"Room created successfully: {room.name} (ID: {room.id})")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Сериализация данных
        serializer = JoinRoomSerializer(data=request.data, context={'request': request, 'room_id': room_id})
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        room = validated_data['room']

        token = request.auth

        # Проверка, является ли пользователь мастером
        is_master = validated_data['is_master']

        if is_master:
            # Мастер может войти при любом статусе комнаты
            PlayerInRoom.objects.get_or_create(
                user_token=token,
                room=room,
                character=None  # Мастер комнаты не привязывается к персонажу
            )
            return Response({"detail": "Master connected to the room"}, status=200)
        else:
            # Игрок может войти только если комната в статусе "Waiting"
            if room.room_status != "Waiting":
                return Response({"detail": "Cannot join the room. The room is not in 'Waiting' status."}, status=400)

            # Проверка, если количество запусков >= 1, то проверяем, был ли игрок уже в комнате
            if room.launches >= 1:
                player_exists = PlayerInRoom.objects.filter(user_token=token, room=room).exists()
                if player_exists:
                    return Response({"detail": "You have already joined this room."}, status=400)

            # Подключение игрока
            character = validated_data['character']
            PlayerInRoom.objects.get_or_create(
                user_token=token,
                room=room,
                character=character
            )
            return Response({"detail": "Player connected to the room"}, status=200)



class CloseRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        token_key = request.headers.get('Authorization')
        if token_key:
            token = Token.objects.get(key=token_key.split()[1])
            user = token.user
        else:
            raise PermissionDenied("Token is missing or invalid.")

        try:
            room = Room.objects.get(id=room_id, master=user)

            # Проверка, закрыта ли комната уже
            if room.room_status == 'Closed':
                return Response({'error': 'Room is already closed.'}, status=status.HTTP_400_BAD_REQUEST)

            # Обновляем статус комнаты
            room.room_status = 'Closed'
            room.save()

            return Response({'message': 'Room closed successfully.'}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)
