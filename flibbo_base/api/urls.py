from django.urls import path
from .views import SupportListCreateView, SupportDetailView

urlpatterns = [
    path('support/', SupportListCreateView.as_view(), name='support-list-create'),
    path('support/<int:pk>/', SupportDetailView.as_view(), name='support-detail'),
]
