from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from my_app.models import Room, Chat, Table, Dice, EntityFigures, PlayerFigures, Character, Stats


class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = ['hp', 'race', 'intelligence', 'strength', 'dexterity', 'constitution', 'wisdom', 'charisma']


class CharacterSerializer(serializers.ModelSerializer):
    stats = StatsSerializer()

    class Meta:
        model = Character
        fields = ['character_name', 'status', 'stats']

    def create(self, validated_data):
        stats_data = validated_data.pop('stats')
        user_token = self.context['request'].auth  # Извлекаем токен из заголовка

        character = Character.objects.create(user_token=user_token, **validated_data)
        Stats.objects.create(character=character, **stats_data)
        return character


class GetRoomSerializer(serializers.ModelSerializer):
    master_token_id = serializers.CharField(source='master_token.key', allow_null=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'room_status', 'master_token_id']

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
