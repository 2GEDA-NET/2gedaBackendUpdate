import os
import chat.routing
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TogedaBackend.settings')

# Configure logging
logger = logging.getLogger(__name__)
logger.debug(f'DJANGO_SETTINGS_MODULE is set to: {os.environ.get("DJANGO_SETTINGS_MODULE")}')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})
