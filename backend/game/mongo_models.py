from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    IntField,
    ListField,
    EmbeddedDocumentField,
)


class MGEntityStats(EmbeddedDocument):
    hp = IntField(required=True)
    level = IntField(required=True)
    intelligence = IntField(required=True)
    resistance = IntField(required=True)
    stability = IntField(required=True)


class MGEntity(Document):
    name = StringField(max_length=100, required=True)
    status = StringField(max_length=50, required=True)
    user_token = StringField(max_length=100)
    meta = {'collection': 'entities'}


class MGCharacterStats(EmbeddedDocument):
    """Характеристики персонажа"""
    hp = IntField(required=True)
    mana = IntField()
    race = StringField(max_length=50)
    intelligence = IntField()
    strength = IntField()
    dexterity = IntField()
    constitution = IntField()
    wisdom = IntField()
    charisma = IntField()
    level = IntField()
    resistance = IntField()
    stability = IntField()


class MGCharacter(Document):
    """Персонажи пользователей"""
    name = StringField(max_length=100, required=True)
    status = StringField(max_length=50)
    user_token = StringField(max_length=100)
    stats = EmbeddedDocumentField(MGCharacterStats)

    meta = {
        'collection': 'characters'
    }


class MGEntityFigures(Document):
    """Фигуры объектов на столе"""
    picture_url = StringField(max_length=100)
    posX = IntField()
    posY = IntField()
    meta = {
        'collection': 'entity_figures'
    }


class MGPlayerFigures(Document):
    """Фигуры игроков на столе"""
    name = StringField(max_length=100)
    picture_url = StringField(max_length=100)
    posX = IntField()
    posY = IntField()
    user_token = StringField(max_length=100)
    meta = {
        'collection': 'player_figures'
    }


class MGItem(EmbeddedDocument):
    """Элемент рюкзака"""
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=500)


class MGBackpack(Document):
    """Рюкзак игрока"""
    user_id = IntField(required=True)
    room_id = IntField(required=True)
    items = ListField(EmbeddedDocumentField(MGItem), default=list)

    meta = {
        'collection': 'backpacks'
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


class MGTable(Document):

    height = IntField(required=True, min_value=0, verbose_name="Height (Высота)")
    length = IntField(required=True, min_value=0, verbose_name="Length (Длина)")

    def __str__(self):
        return f"Dimensions (Height: {self.height}, Length: {self.length})"
