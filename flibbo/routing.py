# your_project/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flibbo.settings')

from django.urls import path
from explore.consumers import ExploreConsumer
from posts.consumers import HomeConsumer
from activity.consumers import ActivityConsumer
websocket_urlpatterns = [
    path('ws/explore/', ExploreConsumer),
    path('ws/home/', HomeConsumer.as_asgi()),
    path('ws/activity/', ActivityConsumer.as_asgi()),


]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})
