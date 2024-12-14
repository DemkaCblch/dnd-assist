import uuid

from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    IntField,
    ListField,
    EmbeddedDocumentField,
)


class MGEntityStats(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    hp = IntField(required=True)
    level = IntField(required=True)
    resistance = IntField(required=True)
    stability = IntField(required=True)


class MGEntity(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    status = StringField(max_length=50, required=True)
    user_token = StringField(max_length=100, required=True)
    stats = EmbeddedDocumentField(MGEntityStats, required=True)


class MGCharacterStats(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    hp = IntField(required=True)
    mana = IntField(required=True)
    race = StringField(max_length=50, required=True)
    intelligence = IntField(required=True)
    strength = IntField(required=True)
    dexterity = IntField(required=True)
    constitution = IntField(required=True)
    wisdom = IntField(required=True)
    charisma = IntField(required=True)
    level = IntField(required=True)
    resistance = IntField(required=True)
    stability = IntField(required=True)


class MGItem(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=500)


class MGBackpack(EmbeddedDocument):
    items = ListField(EmbeddedDocumentField(MGItem), default=list)


class MGCharacter(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    status = StringField(max_length=50, required=True)
    user_token = StringField(max_length=100, required=True)
    stats = EmbeddedDocumentField(MGCharacterStats, required=True)
    backpack = EmbeddedDocumentField(MGBackpack, required=True)


class MGEntityFigures(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    picture_url = StringField(max_length=100, required=True)
    posX = IntField(required=True)
    posY = IntField(required=True)
    entity = EmbeddedDocumentField(MGEntity, required=True)


class MGPlayerFigures(EmbeddedDocument):
    id = StringField(primary_key=True, default=lambda: str(uuid.uuid4()))
    name = StringField(max_length=100, required=True)
    picture_url = StringField(max_length=100, required=True)
    posX = IntField(required=True)
    posY = IntField(required=True)
    user_token = StringField(max_length=100, required=True)
    character = EmbeddedDocumentField(MGCharacter, required=True)


class MGTable(EmbeddedDocument):
    height = IntField(required=True, min_value=0, verbose_name="Height (Высота)")
    length = IntField(required=True, min_value=0, verbose_name="Length (Длина)")


class MGRoom(Document):
    name = StringField(max_length=50, required=True)
    room_status = StringField(default="Waiting", max_length=50, required=True)
    master_token = StringField(required=True)
    user_tokens = ListField(StringField(), default=[])
    current_move = StringField(max_length=100, required=True)

    # Вложенные данные
    player_figures = ListField(EmbeddedDocumentField(MGPlayerFigures), default=[])
    entity_figures = ListField(EmbeddedDocumentField(MGEntityFigures), default=[])
    table = EmbeddedDocumentField(MGTable, required=True)

    meta = {
        'collection': 'rooms'
    }
