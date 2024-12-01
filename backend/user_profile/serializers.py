from rest_framework import serializers
from rest_framework.authtoken.admin import User

from user_profile.models import CharacterStats, Character, EntityStats, Entity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'date_joined']


class CharacterStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterStats
        fields = ['hp', 'race', 'level', 'intelligence', 'strength', 'dexterity', 'constitution', 'wisdom',
                  'resistance', 'stability', 'charisma']


class EntityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityStats
        fields = ['hp', 'level', 'resistance', 'stability']


class CharacterSerializer(serializers.ModelSerializer):
    character_stats = CharacterStatsSerializer()  # Вложенный сериализатор

    class Meta:
        model = Character
        fields = ['id', 'name', 'status', 'character_stats']

    def create(self, validated_data):
        # Извлекаем вложенные данные статистики
        character_stats_data = validated_data.pop('character_stats')

        # Извлекаем токен пользователя из контекста
        user_token = self.context['request'].auth
        if not user_token:
            raise serializers.ValidationError("Invalid token provided.")

        character = Character.objects.create(user_token=user_token, **validated_data)
        CharacterStats.objects.create(character=character, **character_stats_data)

        return character

    def update(self, instance, validated_data):
        # Обновление вложенных данных (если есть)
        character_stats_data = validated_data.pop('character_stats', None)
        if character_stats_data and instance.character_stats:
            stats_serializer = CharacterStatsSerializer(instance.character_stats, data=character_stats_data)
            stats_serializer.is_valid(raise_exception=True)
            stats_serializer.save()

        # Обновление данных самого объекта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class EntitySerializer(serializers.ModelSerializer):
    # Вкладываем статистику в основной сериализатор
    entity_stats = EntityStatsSerializer()

    class Meta:
        model = Entity
        fields = ['id', 'name', 'status', 'entity_stats']

    def create(self, validated_data):
        # Извлекаем статистику, если она есть
        entity_stats_data = validated_data.pop('entity_stats', {})

        user_token = self.context['request'].auth  # Извлекаем токен из заголовка
        if not user_token:
            raise serializers.ValidationError("Invalid token provided.")

        entity = Entity.objects.create(user_token=user_token, **validated_data)
        EntityStats.objects.create(entity=entity, **entity_stats_data)

        return entity

    def update(self, instance, validated_data):
        entity_stats_data = validated_data.pop('entity_stats', None)
        if entity_stats_data and instance.entity_stats:
            EntityStatsSerializer(instance.entity_stats, data=entity_stats_data).is_valid(raise_exception=True)
            EntityStatsSerializer(instance.entity_stats, data=entity_stats_data).save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
