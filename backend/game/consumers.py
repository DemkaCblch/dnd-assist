import json
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from game.utils import transfer_game_data_to_mongodb
from room.models import Room, PlayerInRoom


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Проверяем авторизацию пользователя
        user = self.scope.get("user", None)
        token_key = self.scope.get("token", None)

        if not user or not user.is_authenticated:
            await self.close()
            return

        # Извлекаем room_id из URL
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        try:
            # Проверяем, существует ли комната
            room_exists = await self.check_room_exists(self.room_id)
            if not room_exists:
                print(f"Room with ID {self.room_id} not found.")
                await self.close()
                return

            # Получаем токен мастера комнаты
            master_token = await self.get_master_token(self.room_id)

            # Проверяем, является ли пользователь мастером
            is_master = (token_key == master_token)

            # Добавляем пользователя в PlayerInRoom
            await self.add_player_to_room(user, token_key, self.room_id, is_master)

            # Подключаем пользователя к группе WebSocket
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            print(f"User {user.username} successfully connected to the room {self.room_id}.")

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        # Отключаем пользователя от группы WebSocket
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"Пользователь отключился от комнаты {self.room_id}.")

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return Room.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def get_master_token(self, room_id):
        room = Room.objects.get(id=room_id)
        return room.master_token

    @database_sync_to_async
    def add_player_to_room(self, user, token_key, room_id, is_master=False, character=None):
        room = Room.objects.get(id=room_id)
        token = Token.objects.get(key=token_key)

        if is_master:
            if room.master_token:
                print(f"Room  {room_id} already has a master.")
                return False
            room.master_token = token.key
            room.save()
            print(f"Master {user.username} successfully added to the room {room_id}.")
            return True

        if PlayerInRoom.objects.filter(user_token=token, room=room).exists():
            print(f"Player with the token {token_key} already in the room {room_id}.")
            return False

        PlayerInRoom.objects.create(
            user_token=token,
            room=room,
            character=character,
            is_master=is_master
        )
        print(f"Игрок {user.username} successfully added to the room {room_id}.")
        return True

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == "start_game":
            room_id = self.room_id
            user = self.scope["user"]

            try:
                # Получаем комнату с помощью sync_to_async
                room = await sync_to_async(Room.objects.get)(id=room_id)

                # Получаем токен мастера комнаты с помощью sync_to_async
                master_token = await sync_to_async(lambda: str(room.master_token))()

                # Получаем токен текущего пользователя
                user_token = self.scope.get("token", None)

                # Сравниваем токен мастера с токеном пользователя
                if master_token != user_token:
                    await self.send(text_data=json.dumps({
                        'message': "You are not master."
                    }))
                    return

            except Room.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'message': "Room no find."
                }))
                return

            # Проверяем количество игроков в комнате
            players_in_room_qs = await sync_to_async(PlayerInRoom.objects.filter)(room=room)
            players_count = await sync_to_async(players_in_room_qs.count)()
            if players_count == 0:
                await self.send(text_data=json.dumps({
                    'message': "No have player to start."
                }))
                return

            # Начинаем игру
            await sync_to_async(transfer_game_data_to_mongodb)(room_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_event',
                    'message': f"Game start! {user.username}.",
                    'current_turn': user.username,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def game_event(self, event):
        message = event['message']
        current_turn = event['current_turn']
        await self.send(text_data=json.dumps({
            'message': message,
            'current_turn': current_turn
        }))
