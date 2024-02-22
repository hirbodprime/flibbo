from django.urls import path
from . import views as v


urlpatterns = [
    path('heygen/video/caption/get/<str:video_id>/', v.HeyGenGetVideoCaptionView.as_view(), name='get-caption-video-heygen'),
    path('heygen/video/caption/create/<str:video_id>/', v.HeyGenCreateVideoCaptionView.as_view(), name='create-caption-video-heygen'),
    path('heygen/video/get/<str:video_id>/', v.HeyGenGetVideoView.as_view(), name='voices-list-heygen'),
    path('heygen/video/create/', v.HeyGenCreateVideoView.as_view(), name='create-video-heygen'),
    path('heygen/video/translate/get/<str:video_id>/', v.HeyGenGetVideoTranslateStatusView.as_view(), name='create-video-translate-heygen'),
    path('heygen/video/translate/create/', v.HeyGenCreateVideoTranslateView.as_view(), name='create-video-translate-heygen'),
    path('heygen/translate/languages/list/', v.HeyGenGetLanguagesListTranslateView.as_view(), name='traslate-languages-list-heygen'),
    path('heygen/avatars/list/', v.HeyGenGetAvatarsView.as_view(), name='avatars-list-heygen'),
    path('heygen/voices/list/', v.HeyGenGetVoicesView.as_view(), name='voices-list-heygen'),
    path('heygen/talking-photo/upload/', v.HeyGenTalkingImageUploadView.as_view(), name='heygen-talking-photo-image-upload'),
    path('heygen/talking-photo/list/', v.HeyGenListTalkingPhotoAPIView.as_view(), name='heygen-talking-photo-list'),

    path('studio/presenter/driver/get/<str:presenter_id>/', v.GetPresenterDriversView.as_view(), name='get_presenter_drivers'),
    path('studio/presenters/get/<int:limit>/', v.GetPresentersView.as_view(), name='get_presenters'),
    path('studio/talk/get/<str:talk_id>/', v.GetTalkView.as_view(), name='get_talk'),
    path('studio/talk/create/', v.CreateTalkView.as_view(), name='studio-create-talk'),
    path('studio/talk/images/list/', v.TalkImagesListAPIView.as_view(), name='studio-talk-images'),
    path('studio/talk/languages/list/', v.TalkVoiceActorListAPIView.as_view(), name='talk-voice-actor-list'),
    path('studio/clip/get/<str:clip_id>/', v.GetClipView.as_view(), name='get_talk'),
    path('studio/clip/create/', v.CreateClipView.as_view(), name='studio-create-clip'),
    path('studio/animation/get/<str:animation_id>/', v.GetAnimationView.as_view(), name='studio-create-animation'),
    path('studio/animation/create/', v.CreateAnimationView.as_view(), name='studio-create-animation'),
    path('studio/voices/list/', v.VoiceActorListView.as_view(), name='fliki-video-status'),

    path('fliki/video/status/',v.GetStatusVideoView.as_view(), name='fliki-video-status'),
    path('fliki/video/create/', v.CreateVideoFlikiView.as_view(), name='fliki-create-video'),
    path('fliki/image/create/', v.CreateTextToImageView.as_view(), name='fliki-create-image'),
    path('fliki/voice/create/', v.CreateTextToSpeechView.as_view(), name='fliki-create-voice'),
    path('fliki/voices/list/<str:language>/<str:gender>/', v.GetVoicesView.as_view(), name='get_languages'),
    path('fliki/languages/list/', v.GetLanguagesView.as_view(), name='get_languages'),
    path('fliki/dialects/list/', v.GetDialectsView.as_view(), name='get_languages'),
    
    path('ai/tools/list/', v.AIToolsListView.as_view(), name='ai-tools-list'),
    path('ai/styles/list/', v.StylesListView.as_view(), name='ai-styles-list'),


    path('categories/', v.CategoriesListAPIView.as_view(), name='ai-categoreis'),
    path('chat-categories/', v.OpenAICategoryListAPIView.as_view(), name='ai-categoreis-chat'),
    path('delete-history/', v.DeleteUserHistory.as_view({'post': 'delete_history'}), name='delete-history'),

    
    path('ai-studio/history/', v.UserAllResponsesView.as_view(), name='user_all_responses'),
    path('history/',v.InteractionListView.as_view()),
    path('history/single/<str:chat_id>/', v.ChatInteractionsView.as_view(), name='chat_interactions'),
    path('history/single/', v.ChatInteractionsView.as_view(), name='chat_interactions'),
    path('delete/chat/<str:chat_id>/', v.delete_chat, name='delete_chat_api'),
    path('text-prompts/', v.get_random_prompts, name='random-prompts'),
    path('image-prompts/', v.get_random_image_prompts, name='random-prompts'),
    path('chat/caption/', v.OpenAIChatCreateDescriptionView.as_view()),
    path('chat-edit/',v.OpenAIImageEditInteractionView.as_view()),
    path('chat/',v.OpenAIChatInteractionView.as_view()),
    path('image2/', v.OpenAIImageShareYourThoughtsInteractionView.as_view(), name='share-your-thoughts'),
    path('image/',v.OpenAIImageInteractionView.as_view()),
    path('audio/',v.OpenAIAudioInteractionView.as_view()),
    path('prompts-text/', v.RandomPromptsAPIView.as_view(), name='prompts-text'),
    path('prompts-image/', v.RandomPromptsImageAPIView.as_view(), name='prompts-images'),

    path('chat/create/',v.OpenAIChatIDCreateView.as_view(), name='openai-chat-create'),
    path('chat/history/', v.OpenAIChatIDHistoryView.as_view(), name='openai-chat-history'),

]
