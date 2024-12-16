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
