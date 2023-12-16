from django.urls import path, include
from .views import delete_account
urlpatterns = [
    path('api/', include('accounts.api.urls')),
    path('delete-account/',delete_account)
]
