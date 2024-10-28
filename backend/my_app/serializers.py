import uuid

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from django.contrib.auth import get_user_model

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
