from django.urls import path
from .views import UsersNftsList

urlpatterns = [
    path('purchase-history/', UsersNftsList.as_view(), name='usersnfts-list'),
]
