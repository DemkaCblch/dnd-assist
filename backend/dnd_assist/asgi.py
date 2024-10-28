import os

from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from my_app.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnd_assist.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(ws_urlpatterns)
    )
})
