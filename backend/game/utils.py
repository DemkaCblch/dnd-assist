from asgiref.sync import sync_to_async

from game.mongo_models import MGRoom, MGCharacterStats, MGCharacter, MGPlayerFigures, MGBackpack, MGTable
from room.models import Room
from user_profile.models import Character


async def migrate_room_to_mongo(room_id):
    try:
        room = await sync_to_async(Room.objects.get)(id=room_id)
        players_in_room = await sync_to_async(list)(room.players_in_room.all())
        master_token = await sync_to_async(lambda: str(room.master_token) if room.master_token else None)()
        user_tokens = await sync_to_async(lambda: [str(player.user_token) for player in players_in_room])()
        characters_with_stats = await sync_to_async(
            lambda: [
                {
                    "name": character.name,
                    "status": character.status,
                    "user_token": str(character.user_token.key),
                    "stats": {
                        "hp": character.character_stats.hp,
                        "mana": character.character_stats.mana,
                        "race": character.character_stats.race,
                        "intelligence": character.character_stats.intelligence,
                        "strength": character.character_stats.strength,
                        "dexterity": character.character_stats.dexterity,
                        "constitution": character.character_stats.constitution,
                        "wisdom": character.character_stats.wisdom,
                        "charisma": character.character_stats.charisma,
                        "level": character.character_stats.level,
                        "resistance": character.character_stats.resistance,
                        "stability": character.character_stats.stability,
                    }
                }
                for character in Character.objects.select_related('character_stats')
            ]
        )()
        players_figures = [
            MGPlayerFigures(
                name=char_data["name"],
                picture_url="placeholder_url",  # Здесь можно заменить на реальный URL или поле
                posX=1,  # Начальные координаты, заменить на нужные значения
                posY=1,  # Начальные координаты, заменить на нужные значения
                user_token=char_data["user_token"],
                character=MGCharacter(
                    name=char_data["name"],
                    status=char_data["status"],
                    user_token=char_data["user_token"],
                    backpack=MGBackpack(),  # Пустой рюкзак на начало
                    stats=MGCharacterStats(**char_data["stats"])
                )
            )
            for char_data in characters_with_stats
        ]
        mongo_room = MGRoom(
            name=room.name,
            room_status="InProgress",
            master_token=master_token,
            user_tokens=user_tokens,
            current_move=master_token,
            player_figures=players_figures,
            table=MGTable(height=5, length=5)
        )
        await sync_to_async(mongo_room.save)()

        print(f"Room '{room.name}' migrated with ID {mongo_room.id}")
    except Exception as e:
        print(f"Error migrating room '{room_id}': {e}")
