from rest_framework import serializers, viewsets

from my_app.models import *


class CharacterStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = ['hp', 'race', 'intelligence', 'strength', 'dexterity', 'constitution', 'wisdom', 'charisma']


class CharacterSerializer(serializers.ModelSerializer):
    stats = CharacterStatsSerializer()

    class Meta:
        model = Character
        fields = ['character_name', 'status', 'user', 'stats']

    def create(self, validated_data):
        stats_data = validated_data.pop('stats')
        character = Character.objects.create(**validated_data)
        Stats.objects.create(character=character, **stats_data)
        return character


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

    def create(self, validated_data):
        # В этом месте можно добавить логику для установки статуса и пользователя
        # Предполагается, что master (пользователь) передается из request.user
        validated_data['master'] = self.context['request'].user
        validated_data['room_status'] = 'waiting'  # или другой статус по умолчанию
        validated_data['rooms_list'] = RoomsList.objects.get(id=1)
        return super().create(validated_data)
