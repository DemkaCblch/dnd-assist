from channels.db import database_sync_to_async

from my_app.models import *
from my_app.mongo_models import *


from my_app.models import Room, Character, Stats
from my_app.mongo_models import (
    MGCharacter,
    MGStats,
    MGRoom,
)
from django.core.exceptions import ObjectDoesNotExist


def test123(room_id):
    # Получаем комнату из PostgreSQL
    room = Room.objects.get(id=room_id)
    # Создаем объект комнаты в MongoDB
    mongo_room = MGRoom(
        name=room.name,
        room_status="in_progress",
        master_id=str(room.master.id)
    )
    mongo_room.save()


from bson import ObjectId
from mongoengine.errors import ValidationError

def transfer_game_data_to_mongodb(room_id):
    # Шаг 1: Получаем комнату по заданному ID
    room = Room.objects.get(id=room_id)

    # Шаг 2: Перенос данных о комнате (Room)
    try:
        players_in_room = room.players_in_room.all()  # Все игроки в комнате

        master_token = room.master_token  # Просто берем строку токена
        master_token = str(master_token)
        # Получаем токены всех пользователей
        user_tokens = [player.user_token.key for player in players_in_room]

        mongo_room = MGRoom(
            name=room.name,
            room_status=room.room_status,
            master_token=master_token,  # Токен мастера как строка
            user_token=user_tokens  # Список токенов пользователей как строки
        )
        mongo_room.save()
        print(f"Room '{room.name}' migrated with ID {mongo_room.id}")
    except ValidationError as ve:
        print(f"Validation error while saving room '{room.name}': {ve}")
        return
    except Exception as e:
        print(f"Error saving room '{room.name}': {e}")
        return

    # Шаг 3: Перенос персонажей (Character) для пользователей этой комнаты
    for player_in_room in players_in_room:
        character = player_in_room.character
        if not character:
            print(f"Player in room {room_id} has no character, skipping.")
            continue

        stats = character.stats

        mongo_stats = MGStats(
            hp=stats.hp,
            race=stats.race,
            intelligence=stats.intelligence,
            strength=stats.strength,
            dexterity=stats.dexterity,
            constitution=stats.constitution,
            wisdom=stats.wisdom,
            charisma=stats.charisma
        ) if stats else None

        try:
            mongo_character = MGCharacter(
                character_name=character.character_name,
                status=character.status,
                user_token=str(player_in_room.user_token),  # Сохраняем токен как строку
                stats=mongo_stats
            )
            mongo_character.save()
            print(f"Character '{character.character_name}' migrated with ID {mongo_character.id}")
        except Exception as e:
            print(f"Error saving character '{character.character_name}': {e}")


    # Шаг 4: Перенос фигур объектов (EntityFigures)
    entity_figures = EntityFigures.objects.filter(table__room=room)
    for entity in entity_figures:
        try:
            mongo_entity = MGEntityFigures(
                picture_id=entity.picture_id,
                table_id=entity.table.id
            )
            mongo_entity.save()
            print(f"EntityFigure for user {entity.user.id} migrated with ID {mongo_entity.id}")
        except AttributeError as e:
            print(f"Error fetching token for entity figure: {e}")
        except Exception as e:
            print(f"Error saving entity figure: {e}")

    # Шаг 5: Перенос фигур игроков (PlayerFigures)
    player_figures = PlayerFigures.objects.filter(table__room=room)
    for player_figure in player_figures:
        try:
            mongo_player_figure = MGPlayerFigures(
                name=player_figure.name,
                picture_id=player_figure.picture_id,
                user_token=str(player_figure.user_token),
                table_id=player_figure.table.id
            )
            mongo_player_figure.save()
            print(f"PlayerFigure '{player_figure.name}' migrated with ID {mongo_player_figure.id}")
        except Exception as e:
            print(f"Error saving player figure '{player_figure.name}': {e}")

    print(f"Data migration for room {room_id} completed successfully!")



@database_sync_to_async
def get_room_master(room_id):
    try:
        room = Room.objects.get(id=room_id)
        return room.master_token  # Возвращаем ID мастера комнаты
    except Room.DoesNotExist:
        return None  # В случае ошибки или если комната не найдена
