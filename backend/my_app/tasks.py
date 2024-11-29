from celery import shared_task
from django.core.mail import send_mail
# from .models import .....

@shared_task
def account_created(account_id):
    account = ''
    subject = ''
    message =  'you have successfully registered!'
    mail_sent = send_mail(subject, message, 'admin@dnd-assist.com', [])

    return mail_sent
