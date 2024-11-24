from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        print(f"User found: {token.user}")  # Логируем найденного пользователя
        return token.user
    except Token.DoesNotExist:
        print(f"Token not found for key: {token_key}")  # Логируем, если токен не найден
        return AnonymousUser()



# Определение пользователя по токену до подключения к WS
class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None

        if token_key:
            user = await get_user(token_key)
            if user.is_authenticated:
                scope['user'] = user
                scope['token'] = token_key  # Добавляем токен в scope
            else:
                scope['user'] = AnonymousUser()
                scope['token'] = None  # Если пользователь не найден, то токен будет None
        else:
            scope['user'] = AnonymousUser()
            scope['token'] = None  # Если токен не передан, то токен будет None

        return await super().__call__(scope, receive, send)

