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
    character_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        room_id = self.context['room_id']
        token = self.context['request'].auth

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("Room not found")

        attrs['room'] = room
        attrs['is_master'] = str(room.master_token) == str(token)

        if not attrs['is_master']:
            character_id = attrs.get('character_id')
            if not character_id:
                raise serializers.ValidationError("Character ID is required for players")

            try:
                character = Character.objects.get(id=character_id, user_token=str(token))
                attrs['character'] = character
            except Character.DoesNotExist:
                raise serializers.ValidationError("Character not found or does not belong to the user")

        return attrs


class RoomInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'room_status']
