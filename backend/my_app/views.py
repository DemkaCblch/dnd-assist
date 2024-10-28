from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from my_app.serializers import CharacterSerializer


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
