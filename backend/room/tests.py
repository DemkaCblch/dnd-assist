from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from user_profile.models import Character, CharacterStats
from room.models import Room, PlayerInRoom, Chat
from rest_framework.test import APITestCase


class RoomAPITests(APITestCase):

    def setUp(self):
        self.master_user = User.objects.create_user(username="master_user", password="password")
        self.player_user = User.objects.create_user(username="player_user", password="password")
        self.master_token = Token.objects.create(user=self.master_user)
        self.player_token = Token.objects.create(user=self.player_user)

        self.character = Character.objects.create(
            name="Test Character",
            status="Active",
            user_token=self.player_token
        )
        CharacterStats.objects.create(
            character=self.character,
            hp=100,
            mana=50,
            race="Human",
            level=1,
            intelligence=10,
            strength=15,
            dexterity=12,
            constitution=14,
            wisdom=9,
            resistance=8,
            stability=7,
            charisma=6
        )

        self.room = Room.objects.create(name="Test Room", room_status="Waiting", master_token=self.master_token)

    def test_create_room(self):
        data = {
            "name": "New Room",
        }
        url = reverse('create-room')
        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Token {self.master_token.key}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Room")

    def test_get_am_i_master(self):
        url = reverse('is_master', args=[self.room.id])
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.master_token.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_master"], True)

        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.player_token.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_master"], False)

    def test_get_room_info(self):
        url = reverse('get-info-room', args=[self.room.id])
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.master_token.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.room.name)
        self.assertEqual(response.data["room_status"], self.room.room_status)

    def test_get_room_not_found(self):
        url = reverse('get-info-room', args=[9999])
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {self.master_token.key}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_join_room_as_master(self):
        url = reverse('join-room', args=[self.room.id])
        response = self.client.post(url, data=None, HTTP_AUTHORIZATION=f"Token {self.master_token.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Master connected to the room")
        self.assertTrue(PlayerInRoom.objects.filter(user_token=self.master_token, room=self.room).exists())

    def test_join_room_as_player_when_room_is_waiting_status_and_not_restarted_and_send_character_id_not_wasnt_in_room(
            self):
        data = {
            "character_id": self.character.id
        }

        url = reverse('join-room', args=[self.room.id])

        response = self.client.post(url, data, HTTP_AUTHORIZATION=f"Token {self.player_token.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Player connected to the room.")
        self.assertTrue(PlayerInRoom.objects.filter(user_token=self.player_token, room=self.room).exists())

    def test_join_room_as_player_when_room_is_waiting_status_and_not_restarted_and_not_send_character_id(self):
        url = reverse('join-room', args=[self.room.id])

        response = self.client.post(url, data=None, HTTP_AUTHORIZATION=f"Token {self.player_token.key}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Character ID is required for players.")

    def test_join_room_as_player_when_room_is_not_waiting_status(self):
        self.room.room_status = "InProgress"
        self.room.save()

        url = reverse('join-room', args=[self.room.id])
        response = self.client.post(url, data=None, HTTP_AUTHORIZATION=f"Token {self.player_token.key}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Cannot join the room. The room is not in 'Waiting' status.")

    def test_join_room_as_player_when_room_is_waiting_status_and_restarted_and_not_send_character_id_not_was_in_room(
            self):
        PlayerInRoom.objects.create(user_token=self.player_token, room=self.room)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_token.key}")
        response = self.client.post(f'/api/connect-room/{self.room.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "You have already joined this room.")

    def test_join_room_as_player_when_room_is_waiting_status_and_restarted_not_wasnt_in_room(self):
        self.room.launches = 1
        self.room.save()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.player_token.key}")
        response = self.client.post(f'/api/connect-room/{self.room.id}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You are not registered in this game.")


class RoomModelTest(TestCase):

    def setUp(self):
        self.master_user = User.objects.create_user(username="master_user", password="password")
        self.master_token = Token.objects.create(user=self.master_user)

    def test_create_room(self):
        room = Room.objects.create(
            name="Test Room",
            room_status="Waiting",
            master_token=self.master_token,
            launches=0
        )
        self.assertEqual(str(room), f"Room object ({room.id})")

    def test_room_str_method(self):
        room = Room.objects.create(
            name="Test Room",
            room_status="Waiting",
            master_token=self.master_token,
            launches=0
        )
        self.assertEqual(str(room), f"Room object ({room.id})")


class PlayerInRoomModelTest(TestCase):

    def setUp(self):
        self.master_user = User.objects.create_user(username="master_user", password="password")
        self.player_user = User.objects.create_user(username="player_user", password="password")
        self.master_token = Token.objects.create(user=self.master_user)
        self.player_token = Token.objects.create(user=self.player_user)
        self.character = Character.objects.create(
            name="Test Character",
            status="Active",
            user_token=self.player_token
        )
        self.room = Room.objects.create(
            name="Test Room",
            room_status="Waiting",
            master_token=self.master_token,
            launches=0
        )

    def test_create_player_in_room(self):
        player_in_room = PlayerInRoom.objects.create(
            user_token=self.player_token,
            room=self.room,
            character=self.character,
            is_master=False
        )
        self.assertEqual(str(player_in_room),
                         f"PlayerInRoom object ({player_in_room.id})")

    def test_player_in_room_str_method(self):
        player_in_room = PlayerInRoom.objects.create(
            user_token=self.player_token,
            room=self.room,
            character=self.character,
            is_master=False
        )
        self.assertEqual(str(player_in_room),
                         f"PlayerInRoom object ({player_in_room.id})")


class ChatModelTest(TestCase):

    def setUp(self):
        self.master_user = User.objects.create_user(username="master_user", password="password")
        self.master_token = Token.objects.create(user=self.master_user)
        self.room = Room.objects.create(
            name="Test Room",
            room_status="Waiting",
            master_token=self.master_token,
            launches=0
        )

    def test_create_chat(self):
        chat = Chat.objects.create(
            room=self.room
        )
        self.assertEqual(str(chat), f"Chat object ({chat.id})")

    def test_chat_str_method(self):
        chat = Chat.objects.create(
            room=self.room
        )
        self.assertEqual(str(chat), f"Chat object ({chat.id})")
