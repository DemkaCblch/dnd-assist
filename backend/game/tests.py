from django.test import TestCase
from mongoengine import connect
from mongo_models import (
    MGEntityStats,
    MGEntity,
    MGCharacterStats,
    MGItem,
    MGBackpack,
    MGCharacter,
    MGEntityFigures,
    MGPlayerFigures,
    MGRoom,
    MGTable,
)


class MGEntityModelTest(TestCase):
    def setUp(self):
        # Настройка подключения к MongoDB (если необходимо)
        connect(
            db='DNDAssist',
            username='admin',
            password='admin',
            host='localhost',
            port=27017,
            uuidRepresentation="standard"
        )

    """
class MGRoomModelTest(TestCase):
    def test_mg_room_creation(self):
        # Создание комнаты с персонажами, игроками и сущностями
        characterStats = MGCharacterStats(hp=100, mana=50, race="Gnome", intelligence=5, strength=5, dexterity=5,
                                          constitution=5, wisdom=5, charisma=5, level=3, resistance=7, stability=6)
        backpack = MGBackpack(items=[MGItem(name="Potion", description="Restores 50 HP")])
        character1 = MGCharacter(name="Test Character", stats=characterStats, status="Waiting", backpack=backpack,
                                 user_token="user_token_123")
        character2 = MGCharacter(name="Test Character", stats=characterStats, status="Waiting", backpack=backpack,
                                 user_token="user_token_123")
        entityStats = MGEntityStats(hp=100, level=3, resistance=7, stability=6)
        entity1 = MGEntity(name="Test Entity", stats=entityStats, status="Waiting", user_token="user_token_123")
        room = MGRoom(
            name="Test Room", room_status="Waiting", master_token="master_token_123",
            user_tokens=["user_token_123"], current_move="master_move",
            player_figures=[MGPlayerFigures(name="Player 1", picture_url="url_to_image", posX=1, posY=1,
                                            user_token="user_token_123", character=character1),
                            MGPlayerFigures(name="Player 2", picture_url="url_to_image", posX=1, posY=1,
                                            user_token="user_token_456", character=character2)],
            entity_figures=[
                MGEntityFigures(name="Entity 1", picture_url="url_to_image", posX=0, posY=0, entity=entity1),
            ],
            table=MGTable(height=5, length=10)
        )

        # Сохранение и проверка сохранения
        room.save()
        self.assertEqual(room.name, "Test Room")
        self.assertEqual(len(room.player_figures), 2)
        self.assertEqual(room.player_figures[0].name, "Player 1")
      """
