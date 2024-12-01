from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from room.models import Room, PlayerInRoom
from room.serializers import GetRoomSerializer, CreateRoomSerializer, JoinRoomSerializer, RoomInfoSerializer
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


class GetRoomInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound(detail="Room not found.", code=404)

        serializer = RoomInfoSerializer(room)
        return Response(serializer.data, status=200)
