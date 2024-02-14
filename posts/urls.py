from django.urls import path, include
from .admin import book_admin

urlpatterns = [
    path('api/',include('posts.api.urls')),
    path('admin/book/', book_admin.urls),

]
