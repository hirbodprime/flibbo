from django.urls import path
from . import views

urlpatterns = [
    # Other URLs
    path('activity-feed/<str:activity_type_url>/', views.activity_feed, name='api_activity_feed'),
]
