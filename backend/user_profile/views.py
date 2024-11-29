from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from user_profile.serializers import CharacterSerializer


class CreateCharacterAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CharacterSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            character = serializer.save()
            return Response({
                'message': 'Character created successfully',
                'character': CharacterSerializer(character).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
