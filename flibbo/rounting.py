# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

# Import your websocket consumer here

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": URLRouter([
        path("ws/some_path/", YourWebSocketConsumer.as_asgi()),
    ]),
})
