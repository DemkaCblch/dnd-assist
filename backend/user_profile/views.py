from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from user_profile.models import Character, Entity
from user_profile.serializers import CharacterSerializer, UserSerializer, EntitySerializer


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить информацию профиля",
        operation_description="Получение информации о текущем пользователе",
        responses={
            200: openapi.Response(
                description="Информация о пользователе",
                examples={
                    "application/json": {
                        "username": "test_user",
                        "date_joined": "2023-01-01T00:00:00Z",
                    }
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CreateCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создать персонажа",
        operation_description="Создание персонажа для авторизованного пользователя",
        request_body=CharacterSerializer,
        responses={
            201: openapi.Response(
                description="Успешное создание персонажа",
                schema=CharacterSerializer,
            ),
            400: openapi.Response(
                description="Ошибка валидации",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = CharacterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            character = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить персонажей игрока",
        operation_description="Получение списка персонажей пользователя",
        responses={
            200: openapi.Response(
                description="Список персонажей",
                schema=CharacterSerializer(many=True),
            ),
            401: openapi.Response(
                description="Не авторизован",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user_token = request.auth
        characters = Character.objects.filter(user_token=user_token)
        serializer = CharacterSerializer(characters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateEntityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создать сущности",
        operation_description="Создание сущности",
        request_body=EntitySerializer,
        responses={
            201: openapi.Response(
                description="Успешное создание сущности",
                schema=EntitySerializer,
            ),
            400: openapi.Response(
                description="Ошибка валидации",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = EntitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            entity = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetEntityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить сущности игрока",
        operation_description="Получение сущности по токену пользователя",
        responses={
            200: openapi.Response(
                description="Данные сущности",
                schema=EntitySerializer(many=True),  # Указываем many=True для обработки списка сущностей
            ),
            404: openapi.Response(
                description="Сущность не найдена",
                examples={"application/json": {"error": "Entity not found."}},
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        user_token = request.auth
        entities = Entity.objects.filter(user_token=user_token)

        if not entities:
            return Response({"error": "Entity not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EntitySerializer(entities, many=True)
        return Response(serializer.data)


class GetAllEntitiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить все сущности",
        operation_description="Получение всех сущностей",
        responses={
            200: openapi.Response(
                description="Список сущностей",
                schema=EntitySerializer(many=True),
            ),
            404: openapi.Response(
                description="Сущности не найдены",
                examples={"application/json": {"error": "Entity not found."}},
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        entities = Entity.objects.all()
        if entities.exists():
            return Response(EntitySerializer(entities, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Entity not found.'}, status=status.HTTP_404_NOT_FOUND)
