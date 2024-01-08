# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flibbo.settings')
# from django.core.asgi import get_asgi_application
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# import flibbo.routing


# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             flibbo.routing.websocket_urlpatterns
#         )
#     ),
# })
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flibbo.settings')
django_asgi_app = get_asgi_application()

# Now import your routing and other necessary components
from channels.routing import ProtocolTypeRouter, URLRouter
from flibbo.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
