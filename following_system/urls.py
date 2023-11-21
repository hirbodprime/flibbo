from django.urls import path, include


urlpatterns = [
    path('api/',include('following_system.api.urls'))
]
