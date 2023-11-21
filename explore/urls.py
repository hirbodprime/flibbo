from django.urls import path,include

urlpatterns = [
    path('api/', include('explore.api.urls')),
]
