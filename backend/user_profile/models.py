from django.db import models
from rest_framework.authtoken.models import Token


class Entity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='entities')


class EntityStats(models.Model):
    id = models.AutoField(primary_key=True)
    hp = models.IntegerField()
    level = models.IntegerField()
    resistance = models.IntegerField()
    stability = models.IntegerField()
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name='entity_stats')


class Character(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='characters')


class CharacterStats(models.Model):
    id = models.AutoField(primary_key=True)
    hp = models.IntegerField()
    race = models.CharField(max_length=50)
    level = models.IntegerField()
    intelligence = models.IntegerField()
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    constitution = models.IntegerField()
    wisdom = models.IntegerField()
    resistance = models.IntegerField()
    stability = models.IntegerField()
    charisma = models.IntegerField()
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name='character_stats')
