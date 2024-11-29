from django.db import models
from rest_framework.authtoken.models import Token


class Character(models.Model):
    id = models.AutoField(primary_key=True)
    character_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='characters')

class Stats(models.Model):
    id = models.AutoField(primary_key=True)
    hp = models.IntegerField()
    race = models.CharField(max_length=50)
    intelligence = models.IntegerField()
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    constitution = models.IntegerField()
    wisdom = models.IntegerField()
    charisma = models.IntegerField()
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name='stats')