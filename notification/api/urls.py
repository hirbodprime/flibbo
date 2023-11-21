# urls.py
from django.urls import path
from .views import UserDeviceListCreateView,user_device_list,UserDeviceUpdateView

urlpatterns = [
    # path('devices/', user_device_list, name='user-device-list'),
    path('device/create/', UserDeviceListCreateView.as_view(), name='user-device-list-create'),
    # path('device/update/<int:pk>/', UserDeviceUpdateView.as_view(), name='user-device-update'),

    # ... other URL patterns
]
