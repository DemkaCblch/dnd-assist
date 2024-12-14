import json
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from mongoengine import DoesNotExist
from rest_framework.authtoken.models import Token

from game.mongo_models import MGRoom, MGBackpack, MGItem
from game.utils import migrate_room_to_mongo
from room.models import Room, PlayerInRoom


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Обработка подключения клиента."""
        user = self.scope.get("user")
        token_key = self.scope.get("token")

        if not user or not user.is_authenticated:
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        self.is_master = 'null'

        try:
            # Проверяем существование комнаты
            if not await self._room_exists(self.room_id):
                await self.close()
                return

            master_token = await self._get_master_token(self.room_id)
            master_token = str(master_token)
            self.is_master = (token_key == master_token)
            if not self.is_master:
                if not await self._can_join_room(user, token_key, self.room_id):
                    await self.close()
                    return

            # Подключаем клиента к WebSocket-группе
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        """Обработка отключения клиента."""
        if self.is_master:
            await self._handle_master_disconnect()
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Обработка сообщений от клиента."""
        data = json.loads(text_data)
        action = data.get("action")

        try:
            if action == "start_game":
                await self._start_game()
            elif action == "resume_game":
                await self._resume_game()
            elif action == "add_item":
                await self._add_item(data)
            elif action == "remove_item":
                await self._remove_item(data)
            else:
                await self.send(text_data=json.dumps({"message": "Unknown action."}))
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))

    # === Методы для работы с комнатами ===
    @database_sync_to_async
    def _room_exists(self, room_id):
        return Room.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def _get_master_token(self, room_id):
        room = Room.objects.get(id=room_id)
        return str(room.master_token)

    @database_sync_to_async
    def _can_join_room(self, user, token_key, room_id):
        room = Room.objects.get(id=room_id)
        if room.room_status != "Waiting":
            print(f"Player '{token_key}' can't join in room '{room_id}', status '{room.room_status}'!")
            return False
        if not PlayerInRoom.objects.filter(user_token=token_key, room_id=room_id).exists():
            print(f"Player '{token_key}' can join in room '{room_id}', status '{room.room_status}'!")
            return False
        return True

    @database_sync_to_async
    def _add_player(self, token_key, room_id):
        token = Token.objects.get(key=token_key)
        PlayerInRoom.objects.get_or_create(user_token=token, room_id=room_id, is_master=False)

    @database_sync_to_async
    def _handle_master_disconnect(self):
        room = Room.objects.get(id=self.room_id)
        room.room_status = "Saved"
        room.save()
        PlayerInRoom.objects.filter(room=room).delete()

    # === Методы для управления игровым процессом ===
    async def _start_game(self):
        room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        if room.launches != -1:
            master_token = await self._get_master_token(self.room_id)
            if self.scope.get("token") != master_token:
                raise ValueError("You are not the master.")
            has_players = await database_sync_to_async(PlayerInRoom.objects.filter(room=room).exists)()
            if not has_players:
                raise ValueError("No players to start the game.")
            room.room_status = "In Progress"
            room.launches += 1
            await database_sync_to_async(room.save)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "game_event", "message": "Game started!"}
            )
            await migrate_room_to_mongo(room_id=self.room_id)
        else:
            await self.channel_layer.group_send(self.room_group_name, {"type": "game_event",
                                                                       "message": "The game has already been initialized!"}
                                                )

    async def _resume_game(self):
        room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        if room.room_status != "Saved":
            raise ValueError("Game cannot be resumed.")
        room.room_status = "Waiting"
        await database_sync_to_async(room.save)()
        await self.channel_layer.group_send(self.room_group_name, {"type": "game_event", "message": "Game resumed!"})

    # === Методы для работы с инвентарём ===
    async def _add_item(self, data):
        user_id = data["user_id"]
        item_name = data["name"]
        item_description = data["description"]
        room = await database_sync_to_async(MGRoom.objects.get)(room_status="In Progress", user_token__contains=user_id)
        backpack, _ = await database_sync_to_async(MGBackpack.objects.get_or_create)(user_id=user_id, room_id=room.id)
        if any(item.name == item_name for item in backpack.items):
            raise ValueError(f"Item '{item_name}' already exists.")
        backpack.items.append(MGItem(name=item_name, description=item_description))
        await database_sync_to_async(backpack.save)()

    async def _remove_item(self, data):
        user_id = data["user_id"]
        item_name = data["name"]
        room = await database_sync_to_async(MGRoom.objects.get)(room_status="In Progress", user_token__contains=user_id)
        backpack = await database_sync_to_async(MGBackpack.objects.get)(user_id=user_id, room_id=room.id)
        initial_count = len(backpack.items)
        backpack.items = [item for item in backpack.items if item.name != item_name]
        if len(backpack.items) == initial_count:
            raise ValueError(f"Item '{item_name}' not found.")
        await database_sync_to_async(backpack.save)()

    async def game_event(self, event):
        # Логика обработки события game_event
        message = event.get("message", "No message provided")

        # Отправляем данные обратно клиенту
        await self.send(text_data=json.dumps({
            "type": "game_event",
            "message": message,
        }))
