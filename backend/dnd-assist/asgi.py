import os

from channels.auth import AuthMiddlewareStack
from channels.layers import get_channel_layer
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from my_app.middleware import TokenAuthMiddleware
from my_app.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnd_assist.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': TokenAuthMiddleware(
        URLRouter(ws_urlpatterns)
    )
})
channel_layer = get_channel_layer()
