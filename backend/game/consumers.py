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

            # Если пользователь не мастер, проверяем статус комнаты
            if not is_master:
                room_status = await self.get_room_status(self.room_id)
                if room_status != "Waiting":
                    print(f"Room status is '{room_status}'. Joining is not allowed.")
                    await self.close()
                    return

                # Если количество запусков больше или равно 1, проверяем, был ли пользователь в комнате
                launches = await self.get_room_launches(self.room_id)
                if launches >= 1:
                    user_has_joined = await self.has_user_joined(token_key, self.room_id)
                    if user_has_joined:
                        print(f"User {user.username} has already joined this room.")
                        await self.close()
                        return

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
        # Проверяем, если пользователь — мастер
        if self.scope["user"].is_authenticated:
            room_id = self.scope["url_route"]["kwargs"]["room_id"]
            try:
                room = await database_sync_to_async(Room.objects.get)(id=room_id)
                master_token = self.get_master_token(room_id)

                if master_token == self.scope["user"]:
                    # Обновляем статус комнаты
                    room.room_status = "Saved"
                    await database_sync_to_async(room.save)()

                    # Удаляем всех игроков из комнаты
                    await database_sync_to_async(PlayerInRoom.objects.filter(room=room).delete)()

                    # Оповещаем игроков
                    await self.channel_layer.group_send(
                        f"room_{room_id}",
                        {
                            "type": "room_terminated",
                            "message": "The game has been terminated because the master disconnected."
                        }
                    )
            except Room.DoesNotExist:
                pass

        # Удаляем подключение из группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def get_room_status(self, room_id):
        try:
            room = await sync_to_async(Room.objects.get)(id=room_id)
            return room.room_status
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return Room.objects.filter(id=room_id).exists()

    async def get_room_launches(self, room_id):
        room = await database_sync_to_async(Room.objects.get)(id=room_id)
        return room.launches

    @database_sync_to_async
    def has_user_joined(self, user, room_id):
        player = PlayerInRoom.objects.filter(user_token=user, room_id=room_id).exists()
        return player


    @database_sync_to_async
    def get_master_token(self, room_id):
        room = Room.objects.get(id=room_id)
        return str(room.master_token)


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
            room.launches += 1
            # Начинаем игру
            await sync_to_async(transfer_game_data_to_mongodb)(room_id)

            room.room_status = "In Progress"
            room.save()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_event',
                    'message': f"Game start!"
                }
            )
        elif action == "resuming_game":
            room_id = self.room_id
            try:
                # Получаем комнату
                room = await sync_to_async(Room.objects.get)(id=room_id)

                # Проверяем статус комнаты
                if room.room_status == "Saved":
                    # Изменяем статус комнаты на "Waiting"
                    room.room_status = "Waiting"
                    await sync_to_async(room.save)()

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_event',
                            'message': "Game resumed! Room status is now 'Waiting'."
                        }
                    )
                else:
                    await self.send(text_data=json.dumps({
                        'message': f"Cannot resume game. Room status is '{room.room_status}'."
                    }))

            except Room.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'message': "Room not found."
                }))
