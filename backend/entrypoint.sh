#!/bin/bash
python manage.py makemigrations room
python manage.py makemigrations user_profile
python manage.py migrate
celery -A dnd_assist worker --loglevel=info --pool=solo &
python manage.py runserver 0.0.0.0:8000
