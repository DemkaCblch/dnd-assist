from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from mongoengine.errors import ValidationError

from game.mongo_models import MGRoom, MGCharacterStats, MGCharacter, MGPlayerFigures
from room.models import Room


def migrate_room_to_mongo(room_id):
    try:
        # Шаг 1: Получаем комнату
        room = Room.objects.get(id=room_id)

        # Шаг 2: Перенос данных о комнате (Room)
        players_in_room = room.players_in_room.all()
        master_token = str(room.master_token) if room.master_token else None
        user_tokens = [str(player.user_token) for player in players_in_room]

        # Создаем MongoDB объект комнаты
        mongo_room = MGRoom(
            name=room.name,
            room_status="Game running",
            master_token=master_token,
            user_token=user_tokens,
            current_move=master_token,
        )
        mongo_room.save()
        print(f"Room '{room.name}' migrated with ID {mongo_room.id}")
    except Exception as e:
        print(f"Error migrating room '{room_id}': {e}")
        return

    # Шаг 3: Перенос персонажей (Character)
    for player in players_in_room:
        character = player.character
        if not character:
            print(f"Player '{player}' in room {room_id} has no character, skipping.")
            continue

        stats = character.stats
        mongo_stats = None
        if stats:
            mongo_stats = MGCharacterStats(
                hp=stats.hp,
                race=stats.race,
                intelligence=stats.intelligence,
                strength=stats.strength,
                dexterity=stats.dexterity,
                constitution=stats.constitution,
                wisdom=stats.wisdom,
                charisma=stats.charisma
            )

        try:
            mongo_character = MGCharacter(
                name=character.character_name,
                status=character.status,
                user_token=str(player.user_token),
                stats=mongo_stats,
            )
            mongo_character.save()
            print(f"Character '{character.character_name}' migrated with ID {mongo_character.id}")
        except Exception as e:
            print(f"Error saving character '{character.character_name}': {e}")

    # Шаг 4: Перенос фигур игроков (PlayerFigures)
    try:
        for player in players_in_room:
            character = player.character
            if not character:
                print(f"Skipping figure for player '{player}' without character.")
                continue

            # Создаем MongoDB объект фигур
            mongo_player_figure = MGPlayerFigures(
                name=character.character_name,
                picture_url="temp_none",
                user_token=str(player.user_token),
            )
            mongo_player_figure.save()
            print(f"Player figure for '{character.character_name}' migrated successfully.")
    except Exception as e:
        print(f"Error migrating player figures: {e}")

    print(f"Migration for room {room_id} completed successfully!")

