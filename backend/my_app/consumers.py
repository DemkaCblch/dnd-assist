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

    async def connect(self):
        # Проверка аутентификации пользователя
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Получаем ID комнаты из URL
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Проверка существования комнаты с room_status "Waiting"
        try:
            room = await database_sync_to_async(Room.objects.get)(
                id=self.room_id,
                room_status="Waiting"
            )
        except ObjectDoesNotExist:
            await self.close()  # Закрыть соединение, если комната не найдена или статус неверный
            return

        # Присоединяемся к группе комнаты
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

    async def receive(self, text_data):
        # Получаем сообщение от WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Отправляем сообщение в группу комнаты
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope["user"].username
            }
        )

    async def chat_message(self, event):
        # Отправляем сообщение обратно в WebSocket
        message = event['message']
        username = event['username']
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
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
