from celery import shared_task
from channels.db import database_sync_to_async
from django.core.mail import EmailMessage
from mongomock.object_id import ObjectId

from game.mongo_models import MGItem, MGRoom, MGBackpack
from room.models import Room


@shared_task
def delete_item(data):
    figure_id = data["figure_id"]
    mongo_room_id = data["mongo_room_id"]
    id = data["id"]

    MGRoom.objects.filter(
        id=mongo_room_id,
        player_figures__id=figure_id
    ).update_one(
        pull__player_figures__S__character__backpack__items={"id": id}
    )


@shared_task
def add_item(data, uuid_gen):
    figure_id = data["figure_id"]
    mongo_room_id = data["mongo_room_id"]
    item_name = data["name"]
    item_description = data["description"]
    MGRoom.objects.filter(
        id=mongo_room_id,
        player_figures__id=figure_id
    ).update_one(
        push__player_figures__S__character__backpack__items={
            "id": uuid_gen,
            "name": item_name,
            "description": item_description
        }
    )


@shared_task
def change_turn_master(data):
    figure_id = data["figure_id"]
    mongo_room_id = data["mongo_room_id"]
    MGRoom.objects(id=mongo_room_id).update_one(set__current_move=figure_id)


@shared_task
def change_turn_player(data):
    mongo_room_id = data["mongo_room_id"]
    MGRoom.objects(id=mongo_room_id).update_one(set__current_move="Master")


@shared_task
def change_character_stats(data):
    """
    {
        "mongo_room_id": "room_id_value",
        "figure_id": "figure_id_value",
        "stats": {
            "hp": 100,
            "mana": 50,
            "race": "Elf",
            "intelligence": 15,
            "strength": 10,
            "dexterity": 12,
            "constitution": 14,
            "wisdom": 16,
            "charisma": 13,
            "level": 5,
            "resistance": 8,
            "stability": 7
        }
    }
    """

    mongo_room_id = data["mongo_room_id"]
    figure_id = data["figure_id"]
    new_stats = data["stats"]

    MGRoom.objects(id=mongo_room_id, player_figures__id=figure_id).update_one(
        set__player_figures__S__character__stats__hp=new_stats.get("hp"),
        set__player_figures__S__character__stats__mana=new_stats.get("mana"),
        set__player_figures__S__character__stats__race=new_stats.get("race"),
        set__player_figures__S__character__stats__intelligence=new_stats.get("intelligence"),
        set__player_figures__S__character__stats__strength=new_stats.get("strength"),
        set__player_figures__S__character__stats__dexterity=new_stats.get("dexterity"),
        set__player_figures__S__character__stats__constitution=new_stats.get("constitution"),
        set__player_figures__S__character__stats__wisdom=new_stats.get("wisdom"),
        set__player_figures__S__character__stats__charisma=new_stats.get("charisma"),
        set__player_figures__S__character__stats__level=new_stats.get("level"),
        set__player_figures__S__character__stats__resistance=new_stats.get("resistance"),
        set__player_figures__S__character__stats__stability=new_stats.get("stability"))


@shared_task
def change_entity_stats(data):
    mongo_room_id = data["mongo_room_id"]
    figure_id = data["figure_id"]
    new_stats = data["stats"]
    MGRoom.objects(id=mongo_room_id, entity_figures__id=figure_id).update_one(
        set__entity_figures__S__entity__stats__hp=new_stats.get("hp"),
        set__entity_figures__S__entity__stats__level=new_stats.get("level"),
        set__entity_figures__S__entity__stats__resistance=new_stats.get("resistance"),
        set__entity_figures__S__entity__stats__stability=new_stats.get("stability"),
    )


@shared_task
def change_entity_stats(data):
    mongo_room_id = data["mongo_room_id"]
    figure_id = data["figure_id"]
    new_stats = data["stats"]
    MGRoom.objects(id=mongo_room_id, entity_figures__id=figure_id).update_one(
        set__entity_figures__S__entity__stats__hp=new_stats.get("hp"),
        set__entity_figures__S__entity__stats__level=new_stats.get("level"),
        set__entity_figures__S__entity__stats__resistance=new_stats.get("resistance"),
        set__entity_figures__S__entity__stats__stability=new_stats.get("stability"),
    )


@shared_task
def change_figure_position(data):
    mongo_room_id = data["mongo_room_id"]
    figure_id = data["figure_id"]
    new_pos_x = data["posX"]
    new_pos_y = data["posY"]

    MGRoom.objects(id=mongo_room_id, player_figures__id=figure_id).update_one(
        set__player_figures__S__posX=new_pos_x,
        set__player_figures__S__posY=new_pos_y
    )
    updated_player = MGRoom.objects(
        id=mongo_room_id,
        player_figures__id=figure_id
    ).update_one(
        set__player_figures__S__posX=new_pos_x,
        set__player_figures__S__posY=new_pos_y
    )
    if updated_player:
        return f"Player figure {figure_id} updated to position ({new_pos_x}, {new_pos_y})."

    updated_entity = MGRoom.objects(
        id=mongo_room_id,
        entity_figures__id=figure_id
    ).update_one(
        set__entity_figures__S__posX=new_pos_x,
        set__entity_figures__S__posY=new_pos_y
    )
    if updated_entity:
        return f"Entity figure {figure_id} updated to position ({new_pos_x}, {new_pos_y})."


@shared_task
def delete_entity_from_room(data):
    figure_id = data["figure_id"]
    mongo_room_id = data["mongo_room_id"]

    try:
        mongo_room = MGRoom.objects.get(id=mongo_room_id)
        mongo_room.update(
            pull__entity_figures={"id": figure_id}
        )
        print(f"Entity with figure_id '{figure_id}' successfully removed from room '{mongo_room_id}'.")
    except MGRoom.DoesNotExist:
        print(f"Room with ID '{mongo_room_id}' not found.")
    except Exception as e:
        print(f"Error deleting entity with figure_id '{figure_id}': {e}")