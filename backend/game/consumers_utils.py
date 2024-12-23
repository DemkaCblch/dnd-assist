import random

from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token

from game.mongo_models import MGRoom
from room.models import Room, PlayerInRoom


@database_sync_to_async
def _room_exists(room_id):
    return Room.objects.filter(id=room_id).exists()


@database_sync_to_async
def _get_master_token(room_id):
    room = Room.objects.get(id=room_id)
    return str(room.master_token)


@database_sync_to_async
def _can_join_room(token_key, room_id):
    room = Room.objects.get(id=room_id)
    if room.room_status != "Waiting":
        print(f"Player '{token_key}' can't join in room '{room_id}', status '{room.room_status}'!")
        return False
    if not PlayerInRoom.objects.filter(user_token=token_key, room_id=room_id).exists():
        print(f"Player '{token_key}' can join in room '{room_id}', player doesn't exist!")
        return False
    return True


@database_sync_to_async
def _set_player_ws_channel(token_key, room_id, channel_name):
    token = Token.objects.get(key=token_key)
    player = PlayerInRoom.objects.get(user_token=token, room_id=room_id)
    player.websocket_channel_id = channel_name
    player.save()


def _get_character_name(mongo_room_id, user_token):
    room = MGRoom.objects(id=mongo_room_id).only('player_figures').first()
    if room and room.player_figures:
        # Проходим по всем фигурам игроков
        for player_figure in room.player_figures:
            if player_figure.character and player_figure.character.user_token == user_token:
                return player_figure.character.name
    return None


@database_sync_to_async
def _get_websocket_channel_ids(room_id):
    return list(PlayerInRoom.objects.filter(room_id=room_id).values_list('websocket_channel_id', flat=True))


@database_sync_to_async
def _master_disconnect(room_id):
    room = Room.objects.get(id=room_id)
    room.room_status = "Saved"
    room.save()


def _get_figure_id_by_user_token(mongo_room_id, user_token):
    room = MGRoom.objects(id=mongo_room_id).only('player_figures').first()
    for figure in room.player_figures:
        if figure.character and figure.character.user_token == user_token:
            return figure.id


def randomize_1_to_20():
    return random.randint(1, 20)
