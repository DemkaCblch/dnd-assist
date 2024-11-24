from pathlib import Path
import mongoengine
from mongoengine import connect

# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ndiknw)*@+6i=izqgzcwa)(ce$1vf#_3336+8)(*^53_@s_sn@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Определяем список разрешенных хостов для доступа к приложению
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'channels',
    'django.contrib.postgres',
    'rest_framework_swagger',
    'rest_framework',
    'storages',
    'djoser',
    'rest_framework.authtoken',
    'my_app',
]

WSGI_APPLICATION = 'dnd_assist.wsgi.application'
ASGI_APPLICATION = 'dnd_assist.asgi.application'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dnd_assist.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dnd-assist',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': '127.0.0.1',
        # 'HOST': '127.0.0.1' для локали,
        # 'PORT': '5433', для локали
        'PORT': '5432',
    }
}


connect(
    db='DNDAssist',
    username='admin',        # Укажите имя пользователя, если требуется аутентификация
    password='admin',        # Укажите пароль, если требуется аутентификация
    host='localhost',                # Укажите адрес сервера MongoDB
    port=27017                       # Укажите порт MongoDB (по умолчанию 27017)
)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройка Celery для работы с RabbitMQ
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'  # Хранение результатов в Redis
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Кэширование сессий через Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Подключение MinIO
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = 'admin'
AWS_SECRET_ACCESS_KEY = 'admin123'
AWS_STORAGE_BUCKET_NAME = 'dnd-assist-files'
AWS_S3_ENDPOINT_URL = 'http://dnd-assist-minio-1:9000'  # или URL твоего MinIO сервера
AWS_S3_REGION_NAME = ''
AWS_S3_USE_SSL = False  # если MinIO работает без SSL, ставь False
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

MEDIA_URL = f'http://localhost:9000/{AWS_STORAGE_BUCKET_NAME}/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],  # Адрес Redis
        },
    },
}
