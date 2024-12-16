from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from game.mongo_models import MGRoom
from room.models import Room, PlayerInRoom
from room.serializers import GetRoomSerializer, CreateRoomSerializer, JoinRoomSerializer, RoomInfoSerializer, \
    GetAmIMasterSerializer


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
            # PlayerInRoom.objects.get_or_create(
            #     user_token=token,
            #     room=room,
            #     character=None  # Мастер комнаты не привязывается к персонажу
            # )
            return Response({"detail": "Master connected to the room"}, status=200)

        # Игрок может войти только если комната в статусе "Waiting"
        if room.room_status != "Waiting":
            return Response({"detail": "Cannot join the room. The room is not in 'Waiting' status."}, status=400)

        # Проверка, если количество запусков >= 1, то проверяем, был ли игрок уже в комнате
        player_exists = PlayerInRoom.objects.filter(user_token=token, room=room).exists()
        if room.launches >= 1:
            if player_exists:
                return Response({"detail": "You have already joined this room."}, status=400)
            # Если player не был в комнате, запрещаем регистрацию
            else:
                return Response({"detail": "You are not registered in this game."}, status=400)

        elif not player_exists:
            # Если launches == 0 и player не был в комнате, проверяем character_id
            if not validated_data.get('character'):
                return Response({"detail": "Character ID is required for players."}, status=400)
        elif player_exists:
            return Response({"detail": "You have already joined this room."}, status=200)

        # Подключение игрока
        character = validated_data.get('character')
        PlayerInRoom.objects.get_or_create(
            user_token=token,
            room=room,
            character=character
        )
        return Response({"detail": "Player connected to the room."}, status=200)


class GetRoomInfoAPIView(APIView):
    """API для получения информации о комнате."""
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound(detail="Room not found.", code=404)

        serializer = RoomInfoSerializer(room)
        return Response(serializer.data, status=200)


class DeleteRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, *args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Token '):
                return Response(
                    {'error': 'Token not provided or invalid.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            token = auth_header.split(' ')[1]

            room = Room.objects.get(id=room_id)

            if room.master_token_id != token:
                return Response(
                    {'error': 'You are not the master of this room.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if room.mongo_room_id:
                mongoRoom = MGRoom.objects.get(id=room.mongo_room_id)
                mongoRoom.delete()

            with transaction.atomic():
                # Delete records from PlayerInRoom associated with this room
                PlayerInRoom.objects.filter(room_id=room.id).delete()

                room.delete()

            return Response(
                {'message': 'Room and related data successfully deleted.'},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'Room with the specified ID not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class GetAmIMaster(APIView):
    """API для проверки, является ли пользователь мастером комнаты."""

    def get(self, request, room_id, *args, **kwargs):
        user_token = request.headers.get('Authorization')

        if not user_token:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)

        if user_token.startswith("Token "):
            user_token = user_token[len("Token "):]

        data = {"room_id": room_id, "user_token": user_token}
        serializer = GetAmIMasterSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            room = Room.objects.get(id=serializer.validated_data["room_id"])
            is_master = str(room.master_token) == serializer.validated_data["user_token"]
            return Response({"is_master": is_master}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
