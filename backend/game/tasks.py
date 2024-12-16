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
