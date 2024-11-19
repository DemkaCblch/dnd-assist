import json
from random import randint

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from time import sleep

from rest_framework.permissions import IsAuthenticated

# Тест
from my_app.models import Room


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 1000)}))
            sleep(1)


from django.core.exceptions import ObjectDoesNotExist
from my_app.models import Room  # Импортируйте модель комнаты


class RoomConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_id = None
        self.current_turn = None  # Имя текущего игрока
        self.players = []  # Список игроков в комнате

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        try:
            room = await database_sync_to_async(Room.objects.get)(
                id=self.room_id,
                room_status="Waiting"
            )
        except ObjectDoesNotExist:
            await self.close()
            return

        if not self.scope["user"].is_staff:
            self.players.append(self.scope["user"].username)

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
        if self.scope["user"].username in self.players:
            self.players.remove(self.scope["user"].username)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == "send_message":
            message = data.get('message')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': self.scope["user"].username
                }
            )

        elif action == "start_game" and self.scope["user"].is_staff:
            if self.players:
                self.current_turn = self.players[0]
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_event',
                        'message': f"Игра началась! Ход игрока {self.current_turn}.",
                        'current_turn': self.current_turn
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'message': "Нельзя начать игру без игроков."
                }))

        elif action == "end_turn" and self.scope["user"].username == self.current_turn:
            self.current_turn = "master"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_event',
                    'message': "Ход завершён. Мастер выбирает следующего игрока или забирает ход себе.",
                    'current_turn': self.current_turn
                }
            )

        elif action == "next_turn" and self.scope["user"].is_staff:
            next_player = data.get("next_player")
            if next_player in self.players:
                self.current_turn = next_player
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_event',
                        'message': f"Ход передан игроку {self.current_turn}.",
                        'current_turn': self.current_turn
                    }
                )
            else:
                await self.send(text_data=json.dumps({
                    'message': f"Игрок {next_player} не найден в комнате."
                }))

        elif action == "take_turn" and self.scope["user"].is_staff:
            self.current_turn = "master"
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_event',
                    'message': "Мастер забрал ход себе.",
                    'current_turn': self.current_turn
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
