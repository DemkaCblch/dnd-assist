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


class CharacterSerializer(serializers.ModelSerializer):
    stats = CharacterStatsSerializer()  # Вложенный сериализатор

    class Meta:
        model = Character
        fields = ['id', 'name', 'status', 'stats']

    def create(self, validated_data):
        # Извлекаем вложенные данные статистики
        stats_data = validated_data.pop('stats')

        # Извлекаем токен пользователя из контекста
        user_token = self.context['request'].auth
        if not user_token:
            raise serializers.ValidationError("Invalid token provided.")

        # Создаем персонажа
        character = Character.objects.create(user_token=user_token, **validated_data)

        # Создаем статистику персонажа
        CharacterStats.objects.create(character=character, **stats_data)

        return character

    def update(self, instance, validated_data):
        # Обновление вложенных данных статистики
        stats_data = validated_data.pop('stats', None)
        if stats_data:
            CharacterStatsSerializer(instance.stats, data=stats_data).is_valid(raise_exception=True)
            CharacterStatsSerializer(instance.stats, data=stats_data).save()

        # Обновление данных персонажа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class EntitySerializer(serializers.ModelSerializer):
    # Вкладываем статистику в основной сериализатор
    entity_stats = serializers.DictField()

    class Meta:
        model = Entity
        fields = ['id', 'name', 'status', 'user_token', 'entity_stats']

    def create(self, validated_data):
        # Извлекаем статистику, если она есть
        entity_stats_data = validated_data.pop('entity_stats', {})

        # Создаем сущность
        user_token = self.context['request'].auth  # Извлекаем токен из заголовка
        entity = Entity.objects.create(user_token=user_token, **validated_data)

        # Создаем статистику сущности, если она была передана
        if entity_stats_data:
            EntityStats.objects.create(entity=entity, **entity_stats_data)

        return entity

    def update(self, instance):
        # Возвращаем статистику в виде словаря, а не объекта
        representation = super().update(instance)
        if instance.entity_stats:
            representation['entity_stats'] = {
                'hp': instance.entity_stats.hp,
                'level': instance.entity_stats.level,
                'intelligence': instance.entity_stats.intelligence,
                'resistance': instance.entity_stats.resistance,
                'stability': instance.entity_stats.stability,
            }
        return representation
