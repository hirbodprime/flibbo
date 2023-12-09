# your_project/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flibbo.settings')

from django.urls import path
from explore.consumers import ExploreConsumer

websocket_urlpatterns = [
    path('ws/explore/', ExploreConsumer),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})
