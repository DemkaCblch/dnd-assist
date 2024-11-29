from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    IntField,
    ListField,
    EmbeddedDocumentField,
)


class MGStats(EmbeddedDocument):
    """Характеристики персонажа"""
    hp = IntField(required=True)
    race = StringField(max_length=50)
    intelligence = IntField()
    strength = IntField()
    dexterity = IntField()
    constitution = IntField()
    wisdom = IntField()
    charisma = IntField()


class MGCharacter(Document):
    """Персонажи пользователей"""
    character_name = StringField(max_length=100, required=True)
    status = StringField(max_length=50)
    user_token = StringField(max_length=100)
    stats = EmbeddedDocumentField(MGStats)  # Вложенные характеристики

    meta = {
        'collection': 'characters'  # Название коллекции в MongoDB
    }


class MGEntityFigures(Document):
    """Фигуры объектов на столе"""
    picture_id = StringField(max_length=100)
    table_id = IntField(required=True)  # Ссылка на стол (Room/Table)
    posX = IntField()
    posY = IntField()
    meta = {
        'collection': 'entity_figures'
    }


class MGPlayerFigures(Document):
    """Фигуры игроков на столе"""
    name = StringField(max_length=100)
    picture_id = StringField(max_length=100)
    table_id = IntField(required=True)  # Ссылка на стол (Room/Table)
    posX = IntField()
    posY = IntField()
    user_token = StringField(max_length=100)
    meta = {
        'collection': 'player_figures'
    }


class MGRoom(Document):
    """Комната для игры"""
    name = StringField(max_length=50, required=True)
    room_status = StringField(max_length=50)
    master_token = StringField(required=True)  # Ссылка на мастера по токену (строка)
    user_token = ListField(StringField(), default=[])  # Список токенов пользователей (строки)
    current_move = StringField(max_length=100)
    meta = {
        'collection': 'rooms'
    }
