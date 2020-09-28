import re

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django.urls import re_path
from rest_framework.authtoken.models import Token

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_name>\w+)/(?P<room_name>\w+)/$', consumers.ChatConsumer),
]
from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter

from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token_name, token_key = headers[b'authorization'].decode().split()
                if token_name == 'Token':
                    token = Token.objects.get(key=token_key)
                    scope['user'] = token.user
            except Token.DoesNotExist:
                pass
        return self.inner(scope)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

application = ProtocolTypeRouter({

    "websocket": TokenAuthMiddlewareStack(
        URLRouter([
            url(r"", consumers.ChatConsumer),
        ])
    )

})
