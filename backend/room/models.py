from django.db import models
from rest_framework.authtoken.models import Token
from user_profile.models import Character


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    room_status = models.CharField(max_length=50)
    master_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='rooms')
    mongo_room_id = models.CharField()
    launches = models.IntegerField(default=0)


class PlayerInRoom(models.Model):
    id = models.AutoField(primary_key=True)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='player_in_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players_in_room')
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='players_in_room', null=True,
                                  blank=True)
    websocket_channel_id = models.CharField()
    is_master = models.BooleanField(default=False)


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='chats')
