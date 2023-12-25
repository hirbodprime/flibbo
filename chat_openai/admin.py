from django.contrib import admin
from . import models


class OpenAIChatCategoriesAdmin(admin.ModelAdmin):
    pass
class OpenAIChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt', 'gpt_response', 'created_at')

class OpenAIImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt_image', 'gpt_response1', 'created_at')

class OpenAIAudioAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_audio_prompt', 'gpt_response', 'created_at')



admin.site.register(models.VoiceActorModel)
admin.site.register(models.UserAIStudioLimit)
admin.site.register(models.TextToImageResponse)
admin.site.register(models.StyleListModel)
admin.site.register(models.AIToolsModel)
admin.site.register(models.AnimationResponse)
admin.site.register(models.TalkResponse)
admin.site.register(models.ClipResponse)
admin.site.register(models.CategoriesModel)
admin.site.register(models.OpenAIChatCategories)
admin.site.register(models.OpenAIChatInteraction,OpenAIChatAdmin)
admin.site.register(models.OpenAIAudioInteraction,OpenAIAudioAdmin)
admin.site.register(models.OpenAIImageInteraction,OpenAIImageAdmin)
