from django.urls import path
from .views import (get_random_image_prompts,UserAllResponsesView,get_random_prompts,ChatInteractionsView,delete_chat,TalkVoiceActorListAPIView,GetVoicesView,GetDialectsView,GetLanguagesView,CreateTextToImageView,StylesListView,AIToolsListView,CreateTalkView,GetTalkView,GetPresentersView,CreateClipView,GetClipView,GetAnimationView,
    OpenAIChatInteractionView,OpenAIAudioInteractionView,GetPresenterDriversView,CreateAnimationView,
    OpenAIImageInteractionView,InteractionListView,DeleteUserHistory, CategoriesListAPIView,OpenAIChatInteractionViewe,OpenAICategoryListAPIView
    ,CreateVideoFlikiView,GetStatusVideoView,VoiceActorListView,CreateTextToSpeechView,TalkImagesListAPIView,OpenAIChatIDCreateView,OpenAIChatIDHistoryView
)

urlpatterns = [

    path('studio/presenter/driver/get/<str:presenter_id>/', GetPresenterDriversView.as_view(), name='get_presenter_drivers'),
    path('studio/presenters/get/<int:limit>/', GetPresentersView.as_view(), name='get_presenters'),
    path('studio/talk/get/<str:talk_id>/', GetTalkView.as_view(), name='get_talk'),
    path('studio/talk/create/', CreateTalkView.as_view(), name='studio-create-talk'),
    path('studio/talk/images/list/', TalkImagesListAPIView.as_view(), name='studio-talk-images'),
    path('studio/talk/languages/list/', TalkVoiceActorListAPIView.as_view(), name='talk-voice-actor-list'),
    path('studio/clip/get/<str:clip_id>/', GetClipView.as_view(), name='get_talk'),
    path('studio/clip/create/', CreateClipView.as_view(), name='studio-create-clip'),
    path('studio/animation/get/<str:animation_id>/', GetAnimationView.as_view(), name='studio-create-animation'),
    path('studio/animation/create/', CreateAnimationView.as_view(), name='studio-create-animation'),
    path('studio/voices/list/', VoiceActorListView.as_view(), name='fliki-video-status'),

    path('fliki/video/status/', GetStatusVideoView.as_view(), name='fliki-video-status'),
    path('fliki/video/create/', CreateVideoFlikiView.as_view(), name='fliki-create-video'),
    path('fliki/image/create/', CreateTextToImageView.as_view(), name='fliki-create-image'),
    path('fliki/voice/create/', CreateTextToSpeechView.as_view(), name='fliki-create-voice'),
    path('fliki/voices/list/<str:language>/<str:gender>/', GetVoicesView.as_view(), name='get_languages'),
    path('fliki/languages/list/', GetLanguagesView.as_view(), name='get_languages'),
    path('fliki/dialects/list/', GetDialectsView.as_view(), name='get_languages'),
    
    path('ai/tools/list/', AIToolsListView.as_view(), name='ai-tools-list'),
    path('ai/styles/list/', StylesListView.as_view(), name='ai-styles-list'),


    path('categories/', CategoriesListAPIView.as_view(), name='ai-categoreis'),
    path('chat-categories/', OpenAICategoryListAPIView.as_view(), name='ai-categoreis-chat'),
    path('delete-history/', DeleteUserHistory.as_view({'post': 'delete_history'}), name='delete-history'),

    
    path('ai-studio/history/', UserAllResponsesView.as_view(), name='user_all_responses'),
    path('history/',InteractionListView.as_view()),
    path('history/single/<str:chat_id>/', ChatInteractionsView.as_view(), name='chat_interactions'),
    path('history/single/', ChatInteractionsView.as_view(), name='chat_interactions'),
    path('delete/chat/<str:chat_id>/', delete_chat, name='delete_chat_api'),
    path('text-prompts/', get_random_prompts, name='random-prompts'),
    path('image-prompts/', get_random_image_prompts, name='random-prompts'),

    path('chat2/',OpenAIChatInteractionViewe.as_view()),
    path('chat/',OpenAIChatInteractionView.as_view()),
    path('image/',OpenAIImageInteractionView.as_view()),
    path('audio/',OpenAIAudioInteractionView.as_view()),

    path('chat/create/', OpenAIChatIDCreateView.as_view(), name='openai-chat-create'),
    path('chat/history/', OpenAIChatIDHistoryView.as_view(), name='openai-chat-history'),

]
