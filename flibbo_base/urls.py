from django.urls import path, include

urlpatterns = [
    path('api/',include('flibbo_base.api.urls'))
]
