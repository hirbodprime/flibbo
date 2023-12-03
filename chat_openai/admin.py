from django.contrib import admin
from . import models

class OpenAIChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt', 'gpt_response', 'created_at')

class OpenAIImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt_image', 'gpt_response1', 'created_at')

class OpenAIAudioAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_audio_prompt', 'gpt_response', 'created_at')

admin.site.register(models.OpenAIChatInteraction,OpenAIChatAdmin)
admin.site.register(models.OpenAIAudioInteraction,OpenAIAudioAdmin)
admin.site.register(models.OpenAIImageInteraction,OpenAIImageAdmin)
