from django.urls import path,include
from .admin import fliki_ai_admin, studio_admin
urlpatterns = [
    path('api/',include('chat_openai.api.urls')),
    path('admin/studio/', studio_admin.urls),
    path('admin/fliki/', fliki_ai_admin.urls),

]
