from mongoengine.errors import ValidationError

from game.mongo_models import MGRoom, MGCharacterStats, MGCharacter, MGEntityFigures, MGPlayerFigures
from room.models import Room


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
            room_status="Game running",
            master_token=master_token,  # Токен мастера как строка
            user_token=user_tokens,  # Список токенов пользователей как строки
            current_move=master_token,
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

        mongo_stats = MGCharacterStats(
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
                name=character.name,
                status=character.status,
                user_token=str(player_in_room.user_token),  # Сохраняем токен как строку
                stats=mongo_stats
            )
            mongo_character.save()
            print(f"Character '{character.name}' migrated with ID {mongo_character.id}")
        except Exception as e:
            print(f"Error saving character '{character.name}': {e}")

    # Шаг 4: Перенос фигур игроков (PlayerFigures)
    players_in_room = room.players_in_room.objects.filter(room_id=room)
    for player in players_in_room:
        # Извлекаем пользователя, связанного с таблицей
        user = player.user_token
        character = character.objests.filter(player.character_id)
        # Создаем MongoDB объект на основе данных PostgreSQL
        mongo_player_figure = MGPlayerFigures(
            name=character.name,
            picture_url="temp_none",
            user_token=str(user),  # Автоматически заполняем user_token
        )
        # Сохраняем MongoDB объект
        mongo_player_figure.save()

    print(f"Data migration for room {room_id} completed successfully!")
