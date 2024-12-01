from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from user_profile.models import Character, Entity
from user_profile.serializers import CharacterSerializer, UserSerializer, EntitySerializer


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class CreateCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CharacterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            character = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_token = request.auth
        characters = Character.objects.filter(user_token=user_token)
        serializer = CharacterSerializer(characters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateEntityAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = EntitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            entity = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetEntityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_token = request.auth

        try:
            # Находим сущность пользователя по токену
            entity = Entity.objects.get(user_token=user_token)
            return Response(EntitySerializer(entity).data, status=status.HTTP_200_OK)
        except Entity.DoesNotExist:
            return Response({'error': 'Entity not found.'}, status=status.HTTP_404_NOT_FOUND)


class GetAllEntitiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        entities = Entity.objects.all()
        if entities.exists():
            return Response(EntitySerializer(entities, many=True).data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Entity not found.'}, status=status.HTTP_404_NOT_FOUND)
