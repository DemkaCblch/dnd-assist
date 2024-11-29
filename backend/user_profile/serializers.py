from rest_framework import serializers

from user_profile.models import Stats, Character


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
