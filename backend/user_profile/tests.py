from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Entity, Character, EntityStats, CharacterStats


class EntityModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=user)

    def test_create_entity(self):
        entity = Entity.objects.create(
            name="Test Entity",
            status="Active",
            user_token=self.token
        )

        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.status, "Active")
        self.assertEqual(entity.user_token, self.token)


class CharacterModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=user)

    def test_create_character(self):
        character = Character.objects.create(
            name="Test Character",
            status="Alive",
            user_token=self.token
        )

        self.assertEqual(character.name, "Test Character")
        self.assertEqual(character.status, "Alive")
        self.assertEqual(character.user_token, self.token)


class EntityStatsModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=user)
        self.entity = Entity.objects.create(
            name="Test Entity",
            status="Active",
            user_token=self.token
        )

    def test_create_entity_stats(self):
        entity_stats = EntityStats.objects.create(
            hp=100,
            level=1,
            resistance=50,
            stability=30,
            entity=self.entity
        )

        self.assertEqual(entity_stats.hp, 100)
        self.assertEqual(entity_stats.level, 1)
        self.assertEqual(entity_stats.resistance, 50)
        self.assertEqual(entity_stats.stability, 30)
        self.assertEqual(entity_stats.entity, self.entity)


class CharacterStatsModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username='test_user')
        self.token = Token.objects.create(user=user)
        self.character = Character.objects.create(
            name="Test Character",
            status="Alive",
            user_token=self.token
        )

    def test_create_character_stats(self):
        character_stats = CharacterStats.objects.create(
            hp=150,
            mana=50,
            race="Human",
            level=5,
            intelligence=10,
            strength=12,
            dexterity=14,
            constitution=10,
            wisdom=9,
            resistance=7,
            stability=8,
            charisma=11,
            character=self.character
        )

        self.assertEqual(character_stats.hp, 150)
        self.assertEqual(character_stats.mana, 50)
        self.assertEqual(character_stats.race, "Human")
        self.assertEqual(character_stats.level, 5)
        self.assertEqual(character_stats.intelligence, 10)
        self.assertEqual(character_stats.strength, 12)
        self.assertEqual(character_stats.dexterity, 14)
        self.assertEqual(character_stats.constitution, 10)
        self.assertEqual(character_stats.wisdom, 9)
        self.assertEqual(character_stats.resistance, 7)
        self.assertEqual(character_stats.stability, 8)
        self.assertEqual(character_stats.charisma, 11)
        self.assertEqual(character_stats.character, self.character)
