from django.urls import path,include

urlpatterns = [
    path('api/',include('chat_openai.api.urls'))
]
