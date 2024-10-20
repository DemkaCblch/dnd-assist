from django.contrib.auth.models import User
from django.db import models

from django.db import models
from django.contrib.auth.models import User


class RoomsList(models.Model):
    id = models.AutoField(primary_key=True)


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    room_status = models.CharField(max_length=50)
    master = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms')
    rooms_list = models.ForeignKey(RoomsList, on_delete=models.CASCADE, related_name='rooms')


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='game')


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='chat')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chats')


class Table(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='table')


class Dice(models.Model):
    id = models.AutoField(primary_key=True)
    dice_type = models.CharField(max_length=50)
    table = models.OneToOneField(Table, on_delete=models.CASCADE, related_name='dice')


class EntityFigures(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entity_figures')
    picture_id = models.CharField(max_length=100)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='entity_figures')

    def __str__(self):
        return f"Entity Figure {self.id} for User {self.user.username}"


class PlayerFigures(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    picture_id = models.CharField(max_length=100)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='player_figures')


class Character(models.Model):
    character_name = models.CharField(max_length=100)
    global_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')

    def __str__(self):
        return self.character_name


class Stats(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE, related_name='stats')
    hp = models.IntegerField()
    race = models.CharField(max_length=50)
    intelligence = models.IntegerField()
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    constitution = models.IntegerField()
    wisdom = models.IntegerField()
    charisma = models.IntegerField()
