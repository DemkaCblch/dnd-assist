from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from room.models import Room, PlayerInRoom
from room.serializers import GetRoomSerializer, CreateRoomSerializer, JoinRoomSerializer, RoomInfoSerializer, \
    GetAmIMasterSerializer


class GetRoomsAPIView(ListAPIView):
    serializer_class = GetRoomSerializer
    queryset = Room.objects.all()

    @swagger_auto_schema(
        operation_summary="Получить список комнат",
        operation_description="Возвращает список всех существующих комнат.",
        responses={200: GetRoomSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создать комнату",
        operation_description="Создает новую комнату. Только авторизованный пользователь может выполнить этот запрос.",
        request_body=CreateRoomSerializer,
        responses={
            201: CreateRoomSerializer,
            400: "Неверные данные"
        }
    )
    def post(self, request):
        serializer = CreateRoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            room = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Присоединиться к комнате",
        operation_description="Позволяет игроку или мастеру присоединиться к комнате.",
        request_body=JoinRoomSerializer,
        responses={
            200: openapi.Response("Успешное подключение к комнате"),
            400: "Ошибка запроса"
        }
    )
    def post(self, request, room_id):
        serializer = JoinRoomSerializer(data=request.data, context={'request': request, 'room_id': room_id})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        room = validated_data['room']
        token = request.auth
        is_master = validated_data['is_master']

        if is_master:
            return Response({"detail": "Master connected to the room"}, status=200)

        if room.room_status != "Waiting":
            return Response({"detail": "Cannot join the room. The room is not in 'Waiting' status."}, status=400)

        player_exists = PlayerInRoom.objects.filter(user_token=token, room=room).exists()
        if room.launches >= 1:
            if player_exists:
                return Response({"detail": "You have already joined this room."}, status=400)
            else:
                return Response({"detail": "You are not registered in this game."}, status=400)

        character = validated_data.get('character')
        PlayerInRoom.objects.get_or_create(
            user_token=token,
            room=room,
            character=character
        )
        return Response({"detail": "Player connected to the room."}, status=200)


class GetRoomInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить информацию о комнате",
        operation_description="Возвращает данные о конкретной комнате по её ID.",
        responses={
            200: RoomInfoSerializer,
            404: "Комната не найдена"
        }
    )
    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found."}, status=404)

        serializer = RoomInfoSerializer(room)
        return Response(serializer.data, status=200)


class DeleteRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Удалить комнату",
        operation_description="Удаляет комнату и связанные с ней данные. Только мастер комнаты может выполнить этот "
                              "запрос.",
        responses={
            200: "Комната успешно удалена",
            401: "Ошибка аутентификации",
            403: "Доступ запрещен",
            404: "Комната не найдена"
        }
    )
    def delete(self, request, room_id):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Token '):
                return Response({'error': 'Token not provided or invalid.'}, status=401)
            token = auth_header.split(' ')[1]

            room = Room.objects.get(id=room_id)
            if str(room.master_token) != token:
                return Response({'error': 'You are not the master of this room.'}, status=403)

            room.delete()
            return Response({'message': 'Room and related data successfully deleted.'}, status=200)
        except ObjectDoesNotExist:
            return Response({'error': 'Room with the specified ID not found.'}, status=404)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class GetAmIMasterAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Проверка, является ли пользователь мастером комнаты",
        operation_description="Возвращает, является ли пользователь мастером указанной комнаты.",
        responses={
            200: openapi.Response("Результат проверки", examples={"application/json": {"is_master": True}}),
            400: "Некорректные данные",
            404: "Комната не найдена"
        }
    )
    def get(self, request, room_id):
        user_token = request.headers.get('Authorization')
        if not user_token:
            return Response({"error": "Authorization header is missing"}, status=400)

        if user_token.startswith("Token "):
            user_token = user_token[len("Token "):]

        data = {"room_id": room_id, "user_token": user_token}
        serializer = GetAmIMasterSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            room = Room.objects.get(id=serializer.validated_data["room_id"])
            is_master = str(room.master_token) == serializer.validated_data["user_token"]
            return Response({"is_master": is_master}, status=200)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)