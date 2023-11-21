# urls.py

from django.urls import path, include
from .views import get_user_ip_view

urlpatterns = [
    # ... other url patterns
    path('api/', include('notification.api.urls')),
    path('get-ip/',get_user_ip_view ),
]
