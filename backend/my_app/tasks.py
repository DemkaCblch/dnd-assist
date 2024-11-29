from celery import shared_task
from django.core.mail import send_mail
# from .models import .....

@shared_task
def account_created():
    pass
