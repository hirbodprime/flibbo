from django.urls import path
from message_system.consumers import ChatConsumer
from explore.consumers import ExploreConsumer

# Define websocket_urlpatterns
websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),
    path("ws/explore/", ExploreConsumer.as_asgi()),
]
