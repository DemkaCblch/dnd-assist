from django.db import models
from rest_framework.authtoken.models import Token


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    room_status = models.CharField(max_length=50)
    master_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='rooms')


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chats')


class Table(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='table')


class Dice(models.Model):
    id = models.AutoField(primary_key=True)
    dice_type = models.CharField(max_length=50)
    table = models.OneToOneField(Table, on_delete=models.CASCADE, related_name='dice')


class EntityFigures(models.Model):
    id = models.AutoField(primary_key=True)
    picture_id = models.CharField(max_length=100)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='entity_figures')


class PlayerFigures(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='player_figures')
    picture_id = models.CharField(max_length=100)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='player_figures')


class Character(models.Model):
    id = models.AutoField(primary_key=True)
    character_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='characters')


class PlayerInRoom(models.Model):
    id = models.AutoField(primary_key=True)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='player_in_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players_in_room')
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='players_in_room', null=True, blank=True)
    is_master = models.BooleanField(default=False)



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
