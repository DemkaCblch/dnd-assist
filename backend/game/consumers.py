import asyncio
import json
import uuid

from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from mongoengine import DoesNotExist
from rest_framework.authtoken.models import Token

from game.consumers_utils import _room_exists, _get_master_token, _can_join_room, _set_player_ws_channel, \
    _get_character_name, get_websocket_channel_ids, get_figure_id_by_user_token
from game.tasks import add_item, delete_item, change_turn_master, change_turn_player, change_character_stats, \
    change_figure_position
from game.consumers_utils import master_disconnect
from game.mongo_models import MGRoom
from game.utils import migrate_room_to_mongo, fetch_room_data
from room.models import Room, PlayerInRoom


class RoomConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.token_key = None
        self.mongo_room_id = None

    async def connect(self):
        """Обработка подключения клиента."""
        user = self.scope.get("user")
        self.token_key = self.scope.get("token")

        if not user or not user.is_authenticated:
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        self.is_master = 'null'

        try:
            # Проверяем существование комнаты
            if not await _room_exists(self.room_id):
                await self.close()
                return

            master_token = await _get_master_token(self.room_id)
            master_token = str(master_token)
            self.is_master = (self.token_key == master_token)
            if not self.is_master:
                if not await _can_join_room(self.token_key, self.room_id):
                    await self.close()
                    return
                await _set_player_ws_channel(self.token_key, self.room_id, self.channel_name)

            room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
            room.room_status = "Waiting"
            await database_sync_to_async(room.save)()

            # Подключаем клиента к WebSocket-группе
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close()

    async def receive(self, text_data):
        """Обработка сообщений от клиента."""
        data = json.loads(text_data)
        action = data.get("action")

        try:
            if action == "start_game":
                await self.start_game()
            elif action == "add_item":
                if self.is_master:
                    uuid_gen = str(uuid.uuid4())
                    add_item.delay(data, uuid_gen)
                    await self.add_item_send_info(data, uuid_gen)
                else:
                    await self.send(text_data=json.dumps({"message": "You are not master!"}))
            elif action == "delete_item":
                if self.is_master:
                    delete_item.delay(data)
                    await self.delete_item_send_info(data)
                else:
                    await self.send(text_data=json.dumps({"message": "You are not master!"}))
            elif action == "change_turn":
                if self.is_master:
                    change_turn_master.delay(data)
                    await self.change_turn_send_info(data["figure_id"])
                else:
                    if MGRoom.objects(id=data["mongo_room_id"]).first().current_move == get_figure_id_by_user_token(
                            mongo_room_id=data["mongo_room_id"], user_token=self.token_key):
                        change_turn_player.delay(data)
                        await self.change_turn_send_info("Master")
                    else:
                        await self.send(text_data=json.dumps({"message": "Now not you turn!"}))
            elif action == "change_character_stats":
                if self.is_master:
                    change_character_stats.delay(data)
                    await self.change_character_stats_send_info(data)
                else:
                    await self.send(text_data=json.dumps({"message": "You are not master!"}))
            elif action == "change_position_figure":
                if self.is_master:
                    change_figure_position.delay(data)
                    await self.change_position_figure_send_info(data)
                else:
                    figure_id = get_figure_id_by_user_token(mongo_room_id=data["mongo_room_id"],
                                                            user_token=self.token_key)
                    if figure_id == data["figure_id"]:
                        change_figure_position.delay(data)
                        await self.change_position_figure_send_info(data)
                    else:
                        await self.send(text_data=json.dumps({"message": "That not you figure!"}))


            else:
                await self.send(text_data=json.dumps({"message": "Unknown action."}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))

    """ === Методы для работы с комнатой === """

    async def start_game(self):
        room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        if room.room_status != "In Progress":
            master_token = await _get_master_token(self.room_id)
            if self.scope.get("token") != master_token:
                raise ValueError("You are not the master.")
            has_players = await database_sync_to_async(PlayerInRoom.objects.filter(room=room).exists)()
            if not has_players:
                raise ValueError("No players to start the game.")
            # room.room_status = "In Progress"
            # room.launches += 1
            await database_sync_to_async(room.save)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "handler_game_event", "message": "Game started!"}
            )
            if room.launches == 0:
                self.mongo_room_id = await migrate_room_to_mongo(room_id=self.room_id)
            # Отослать всем игрокам информацию об игре
            await self.room_data_send_info(self.mongo_room_id)
        else:
            await self.channel_layer.group_send(self.room_group_name, {"type": "handler_game_event",
                                                                       "message": "The game has already started!"})

    async def disconnect(self, close_code):
        """Обработка отключения клиента."""
        if self.is_master:
            await master_disconnect(room_id=self.room_id)
            channel_ids = await get_websocket_channel_ids(self.room_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "handler_master_disconnect"
                }
            )
            await asyncio.sleep(1)
            for channel_name in channel_ids:
                await self.channel_layer.send(channel_name, {
                    "type": "websocket.close",
                    "code": 1000,
                })
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def change_turn_send_info(self, figure_id):
        await self.channel_layer.group_send(self.room_group_name,
                                            {"type": "handler_change_turn_send_info", "figure_id": figure_id})

    async def room_data_send_info(self, mongo_room_id):
        room_data = await database_sync_to_async(fetch_room_data)(mongo_room_id)
        await self.channel_layer.group_send(self.room_group_name,
                                            {"type": "handler_room_data_send_info", "room_data": room_data})

    """ === Методы для работы с фигуркой === """

    async def add_item_send_info(self, data, uuid_gen):
        figure_id = data["figure_id"]
        item_name = data["name"]
        item_description = data["description"]
        await self.channel_layer.group_send(self.room_group_name,
                                            {"type": "handler_add_item_send_info",
                                             "id": uuid_gen,
                                             "figure_id": figure_id,
                                             "item_name": item_name,
                                             "item_description": item_description})

    async def delete_item_send_info(self, data):
        id = data["id"]
        figure_id = data["figure_id"]
        await self.channel_layer.group_send(self.room_group_name,
                                            {"type": "handler_delete_item_send_info",
                                             "id": id,
                                             "figure_id": figure_id})

    async def change_character_stats_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.channel_layer.group_send(self.room_group_name,
                                            {"type": "handler_change_character_stats_send_info",
                                             "mongo_room_id": mongo_room_id,
                                             "figure_id": figure_id,
                                             "hp": data["stats"]["hp"],
                                             "mana": data["stats"]["mana"],
                                             "race": data["stats"]["race"],
                                             "intelligence": data["stats"]["intelligence"],
                                             "strength": data["stats"]["strength"],
                                             "dexterity": data["stats"]["dexterity"],
                                             "constitution": data["stats"]["constitution"],
                                             "wisdom": data["stats"]["wisdom"],
                                             "charisma": data["stats"]["charisma"],
                                             "level": data["stats"]["level"],
                                             "resistance": data["stats"]["resistance"],
                                             "stability": data["stats"]["stability"]

                                             })

    async def change_entity_stats_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "handler_change_entity_stats_send_info",
                "mongo_room_id": mongo_room_id,
                "figure_id": figure_id,
                "stats": {
                    "hp": data["hp"],
                    "level": data["level"],
                    "resistance": data["resistance"],
                    "stability": data["stability"]
                }
            }
        )

    async def change_position_figure_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "handler_change_position_figure_send_info",
                "mongo_room_id": mongo_room_id,
                "figure_id": figure_id,
                "posX": data["posX"],
                "posY": data["posY"]
            }
        )

    """ === Обработчики === """

    async def websocket_close(self, event):
        """Обработчик закрытия WebSocket."""
        code = event.get("code", 1000)
        await self.close(code)

    async def handler_master_disconnect(self, event):
        await self.send(text_data=json.dumps(
            {"type": "master_disconnect", "message": "The room is closing because the admin has left."}))

    async def handler_add_item_send_info(self, event):
        figure_id = event["figure_id"]
        item_name = event["item_name"]
        item_description = event["item_description"]
        uuid_gen = event["id"]

        await self.send(text_data=json.dumps({
            "type": "add_item",
            "id": uuid_gen,
            "figure_id": figure_id,
            "item_name": item_name,
            "item_description": item_description,
        }))

    async def handler_delete_item_send_info(self, event):
        id = event["id"]
        figure_id = event["figure_id"]

        await self.send(text_data=json.dumps({
            "type": "delete_item",
            "id": id,
            "figure_id": figure_id,
        }))

    async def handler_game_event(self, event):
        message = event.get("message", "No message provided")

        await self.send(text_data=json.dumps({
            "type": "game_event",
            "message": message,
        }))

    async def handler_room_data_send_info(self, event):
        room_data = event["room_data"]
        await self.send(text_data=json.dumps({
            "type": "room_data",
            "data": room_data
        }))

    async def handler_change_turn_send_info(self, event):
        character_name = event["name"]
        await self.send(text_data=json.dumps({
            "type": "change_turn",
            "name": character_name
        }))

    async def handler_change_character_stats_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.send(text_data=json.dumps(
            {"type": "change_character_stats",
             "mongo_room_id": mongo_room_id,
             "figure_id": figure_id,
             "stats": {
                 "hp": data["hp"],
                 "mana": data["mana"],
                 "race": data["race"],
                 "intelligence": data["intelligence"],
                 "strength": data["strength"],
                 "dexterity": data["dexterity"],
                 "constitution": data["constitution"],
                 "wisdom": data["wisdom"],
                 "charisma": data["charisma"],
                 "level": data["level"],
                 "resistance": data["resistance"],
                 "stability": data["stability"]
             }}))

    async def handler_change_entity_stats_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.send(
            text_data=json.dumps({
                "type": "change_entity_stats",
                "mongo_room_id": mongo_room_id,
                "figure_id": figure_id,
                "stats": {
                    "hp": data["stats"]["hp"],
                    "level": data["stats"]["level"],
                    "resistance": data["stats"]["resistance"],
                    "stability": data["stats"]["stability"]
                }
            })
        )

    async def handler_change_position_figure_send_info(self, data):
        figure_id = data["figure_id"]
        mongo_room_id = data["mongo_room_id"]
        await self.send(text_data=json.dumps({"type": "change_position_figure",
                                              "mongo_room_id": mongo_room_id,
                                              "figure_id": figure_id,
                                              "posX": data["posX"],
                                              "posY": data["posY"]}))
