import json
from random import randint
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from time import sleep

from djoser.conf import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

# Тест
from my_app.models import Room, PlayerInRoom, Character
from my_app.utils import transfer_game_data_to_mongodb, get_room_master


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 1000)}))
            sleep(1)


from django.core.exceptions import ObjectDoesNotExist
from my_app.models import Room  # Импортируйте модель комнаты


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
            # Получаем токен мастера комнаты
            master_token_id = await self.get_master_token(self.room_id)

            # Проверяем, является ли пользователь мастером
            is_master = (token_key == master_token_id)

            # Добавляем пользователя в PlayerInRoom
            await self.add_player_to_room(user, token_key, self.room_id, is_master)

            # Подключаем пользователя к группе WebSocket
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            print(f"Пользователь {user.username} подключен к комнате {self.room_id}.")

        except Exception as e:
            print(f"Ошибка при подключении: {e}")
            await self.close()

    async def disconnect(self, close_code):
        # Отключаем пользователя от группы WebSocket
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"Пользователь отключился от комнаты {self.room_id}.")

    @database_sync_to_async
    def get_master_token(self, room_id):
        """
        Получает токен мастера комнаты.
        """
        try:
            room = Room.objects.get(id=room_id)
            return room.master_token_id  # Предполагается, что мастер имеет токен
        except ObjectDoesNotExist:
            print(f"Комната с ID {room_id} не найдена.")
            return None

    @database_sync_to_async
    def add_player_to_room(self, user, token_key, room_id, is_master=False, character=None):
        try:
            # Получаем комнату и токен
            room = Room.objects.get(id=room_id)
            token = Token.objects.get(key=token_key)

            # Если это мастер, то не добавляем в PlayerInRoom
            if is_master:
                # Проверяем, если комната уже имеет мастера, не добавляем нового
                if room.master_token:
                    print(f"Room {room_id} already has a master.")
                    return False
                # Присваиваем комнату мастеру
                room.master_token = token.key  # Устанавливаем токен мастера
                room.save()
                print(f"Master {user.username} successfully assigned to room {room_id}.")
                return True

            # Проверяем, есть ли игрок с данным токеном в комнате
            if PlayerInRoom.objects.filter(user_token=token, room=room).exists():
                print(f"Player with token {token_key} is already in the room {room_id}.")
                return False

            # Создаём запись для нового игрока
            player = PlayerInRoom(
                user_token=token,
                room=room,
                character=character,  # Обязательно указываем персонажа
                is_master=is_master
            )
            player.save()
            print(f"Player {user.username} successfully added to room {room_id}.")
            return True

        except Room.DoesNotExist:
            print(f"Room with id {room_id} does not exist.")
            return False
        except Token.DoesNotExist:
            print(f"Token with key {token_key} does not exist.")
            return False

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


class RoomUpdateConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    async def connect(self):
        self.room_group_name = 'room_updates'  # Имя группы для обновлений о комнатах

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Метод для отправки обновлений о состоянии комнат
    async def send_rooms_update(self, rooms):
        await self.channel_layer.group_send(
            'room_updates',
            {
                'type': 'update_rooms',
                'rooms': rooms
            }
        )

    async def update_rooms(self, event):
        rooms = event['rooms']
        await self.send(text_data=json.dumps({
            'rooms': rooms
        }))
