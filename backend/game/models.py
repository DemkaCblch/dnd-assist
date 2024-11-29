from django.db import models
from rest_framework.authtoken.models import Token


class EntityFigures(models.Model):
    id = models.AutoField(primary_key=True)
    picture_url = models.CharField(max_length=100)


class PlayerFigures(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    user_token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name='player_figures')
    picture_url = models.CharField(max_length=100)
