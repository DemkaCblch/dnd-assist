from asgiref.sync import sync_to_async

from game.mongo_models import MGRoom, MGCharacterStats, MGCharacter, MGPlayerFigures, MGBackpack, MGTable, MGEntity, \
    MGEntityStats, MGEntityFigures
from room.models import Room, PlayerInRoom
from user_profile.models import Character, EntityStats, Entity


async def migrate_room_to_mongo(room_id):
    mongo_room_id = ""
    try:
        room = await sync_to_async(Room.objects.get)(id=room_id)
        players_in_room = await sync_to_async(list)(room.players_in_room.all())
        master_token = await sync_to_async(lambda: str(room.master_token) if room.master_token else None)()
        user_tokens = await sync_to_async(lambda: [str(player.user_token) for player in players_in_room])()
        characters_with_stats = await sync_to_async(
            lambda: [
                {
                    "name": character.name,
                    "websocket_channel_id": PlayerInRoom.objects.filter(character_id=character.id,
                                                                        room_id=room_id).first().websocket_channel_id,
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
                for character in
                Character.objects.filter(players_in_room__room_id=room_id).select_related('character_stats')
            ]
        )()
        players_figures = [
            MGPlayerFigures(
                name=char_data["name"],
                picture_url="placeholder_url",  # Здесь можно заменить на реальный URL или поле
                posX=1,  # Начальные координаты, заменить на нужные значения
                posY=1,  # Начальные координаты, заменить на нужные значения
                character=MGCharacter(
                    name=char_data["name"],
                    websocket_channel_id=char_data["websocket_channel_id"],
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
            room_id=room_id,
            room_status="InProgress",
            master_token=master_token,
            user_tokens=user_tokens,
            current_move="Master",
            player_figures=players_figures,
            table=MGTable(height=10, length=20)
        )
        await sync_to_async(mongo_room.save)()
        mongo_room_id = mongo_room.id
        await sync_to_async(lambda: setattr(room, 'mongo_room_id', mongo_room_id) or room.save())()
        await sync_to_async(room.save)()
        print(f"Room '{room.name}' migrated with ID {mongo_room.id}")
    except Exception as e:
        print(f"Error migrating room '{room_id}': {e}")
    return mongo_room_id


async def add_entity_to_room(entity_id, mongo_room_id, posX, posY):
    try:
        entity = await sync_to_async(Entity.objects.get)(id=entity_id)
        entity_stats = await sync_to_async(EntityStats.objects.get)(entity=entity)

        mongo_entity_stats = MGEntityStats(
            hp=entity_stats.hp,
            level=entity_stats.level,
            resistance=entity_stats.resistance,
            stability=entity_stats.stability
        )

        user_token_key = await sync_to_async(lambda: str(entity.user_token.key))()

        mongo_entity = MGEntity(
            name=entity.name,
            status=entity.status,
            user_token=user_token_key,
            stats=mongo_entity_stats
        )

        mongo_entity_figure = MGEntityFigures(
            name=entity.name,
            picture_url="placeholder_url",
            posX=posX,
            posY=posY,
            entity=mongo_entity
        )

        mongo_room = MGRoom.objects.get(id=mongo_room_id)

        mongo_room.update(
            push__entity_figures=mongo_entity_figure
        )

        print(f"Entity '{entity.name}' with stats added to MongoDB room '{mongo_room_id}'.")

        return mongo_entity_figure

    except Exception as e:
        print(f"Error adding entity '{entity_id}' to room '{mongo_room_id}': {e}")


def fetch_room_data(room_id):
    room = MGRoom.objects.get(id=room_id)
    room_dict = {
        "id": str(room.id),
        "name": room.name,
        "room_status": room.room_status,
        "current_move": room.current_move,
        "player_figures": [
            {
                "id": str(player["id"]),
                "name": player["name"],
                "picture_url": player["picture_url"],
                "posX": player["posX"],
                "posY": player["posY"],
                "character": [
                    {
                        "id": str(player["character"]["id"]),
                        "name": player["character"]["name"],
                        "status": player["character"]["status"],
                        "stats": [
                            {
                                "id": str(player["character"]["stats"]["id"]),
                                "hp": player["character"]["stats"]["hp"],
                                "mana": player["character"]["stats"]["mana"],
                                "race": player["character"]["stats"]["race"],
                                "intelligence": player["character"]["stats"]["intelligence"],
                                "strength": player["character"]["stats"]["strength"],
                                "dexterity": player["character"]["stats"]["dexterity"],
                                "constitution": player["character"]["stats"]["constitution"],
                                "wisdom": player["character"]["stats"]["wisdom"],
                                "charisma": player["character"]["stats"]["charisma"],
                                "level": player["character"]["stats"]["level"],
                                "resistance": player["character"]["stats"]["resistance"],
                                "stability": player["character"]["stats"]["stability"]
                            }
                        ]
                    }
                ]

            } for player in room.player_figures
        ],
        "entity_figures": room.entity_figures,
        "table": {
            "height": room.table.height,
            "length": room.table.length
        }
    }
    return room_dict
