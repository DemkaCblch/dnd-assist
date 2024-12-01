from celery import shared_task
from django.core.mail import EmailMessage

from room.models import Room


@shared_task
def check_room_exists(room_id):
    return Room.objects.filter(id=room_id).exists()
