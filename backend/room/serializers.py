from rest_framework.authtoken.models import Token
from rest_framework import serializers
from room.models import Room
from user_profile.models import Character


class GetRoomSerializer(serializers.ModelSerializer):
    master_token = serializers.CharField(source='master_token.key', allow_null=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'room_status', 'master_token']

class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

    def create(self, validated_data):
        # Получаем или создаем токен для текущего пользователя
        user = self.context['request'].user
        token = Token.objects.get_or_create(user=user)[0]  # Получаем токен пользователя

        validated_data['master_token'] = token  # Сохраняем токен в master_token
        validated_data['room_status'] = 'Waiting'  # Устанавливаем статус комнаты по умолчанию

        return super().create(validated_data)


class JoinRoomSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    character_id = serializers.IntegerField()

    def validate(self, attrs):
        room_id = attrs.get('room_id')
        character_id = attrs.get('character_id')
        user = self.context['request'].user  # Здесь также используется user, который берется из токена

        # Проверяем, существует ли комната с данным ID
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found")

        # Проверяем, существует ли персонаж с данным ID и принадлежит ли он текущему пользователю
        try:
            character = Character.objects.get(id=character_id, user=user)  # Тут проверка на user
        except Character.DoesNotExist:
            raise serializers.ValidationError("Character not found or does not belong to the user")

        # Возвращаем валидированные данные
        attrs['room'] = room
        attrs['character'] = character
        return attrs
