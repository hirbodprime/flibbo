from django.contrib import admin
from . import models


class OpenAIChatCategoriesAdmin(admin.ModelAdmin):
    pass
class OpenAIChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt', 'gpt_response', 'created_at','chat')

class OpenAIImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_text_prompt_image', 'gpt_response1', 'created_at')

class OpenAIAudioAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_audio_prompt', 'gpt_response', 'created_at')

class ToolsOptionsModelAdmin(admin.ModelAdmin):
    change_form_template = "custom_admin.html"


admin.site.register(models.OpenAIChatID)
admin.site.register(models.TalkImages)
admin.site.register(models.LanguageAndDialectRelation)
admin.site.register(models.Language)
admin.site.register(models.Dialect)
admin.site.register(models.ToolsOptionsModel,ToolsOptionsModelAdmin)
admin.site.register(models.TextToSpeechResponse)
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
