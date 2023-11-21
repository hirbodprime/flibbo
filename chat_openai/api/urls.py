from django.urls import path
from .views import (
    OpenAIChatInteractionView,OpenAIAudioInteractionView,
    OpenAIImageInteractionView,InteractionListView,DeleteUserHistory
)

urlpatterns = [
    path('delete-history/', UserHistoryViewSet.as_view({'post': 'delete_history'}), name='delete-history'),

    
    path('history/',InteractionListView.as_view()),
    
    path('chat/',OpenAIChatInteractionView.as_view()),
    path('image/',OpenAIImageInteractionView.as_view()),
    path('audio/',OpenAIAudioInteractionView.as_view()),

]
