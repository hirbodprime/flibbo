from django.contrib import admin
from . import models

from django.contrib.admin import AdminSite
from django.contrib.admin import ModelAdmin

class FlikiAIAdmin(AdminSite):
    site_header = 'Fliki AI tools'
    site_title = 'Fliki Tools Admin'

class StudioAIAdmin(AdminSite):
    site_header = 'Studio AI tools'
    site_title = 'Studio Tools Admin'

class OpenAIAdmin(AdminSite):
    site_header = 'OpenAI AI tools'
    site_title = 'OpenAI Tools Admin'

# Repeat for other categories
# studio 





studio_admin = StudioAIAdmin(name='studioaiadmin')
studio_admin.register(models.TalkResponse, ModelAdmin)
studio_admin.register(models.VoiceActorModel, ModelAdmin)
studio_admin.register(models.ClipResponse, ModelAdmin)
studio_admin.register(models.TalkImages, ModelAdmin)
studio_admin.register(models.AnimationResponse, ModelAdmin)
studio_admin.register(models.UserAIStudioLimit, ModelAdmin)






fliki_ai_admin = FlikiAIAdmin(name='flikiaiadmin')
fliki_ai_admin.register(models.LanguageAndDialectRelation, ModelAdmin)
fliki_ai_admin.register(models.Language, ModelAdmin)
fliki_ai_admin.register(models.Dialect, ModelAdmin)
fliki_ai_admin.register(models.ToolsOptionsModel, ModelAdmin)
fliki_ai_admin.register(models.TextToSpeechResponse, ModelAdmin)
fliki_ai_admin.register(models.TextToImageResponse, ModelAdmin)
fliki_ai_admin.register(models.StyleListModel, ModelAdmin)


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
admin.site.register(models.UserAIStudioLimit)

admin.site.register(models.CategoriesModel)
admin.site.register(models.OpenAIChatCategories)
admin.site.register(models.OpenAIChatInteraction,OpenAIChatAdmin)
admin.site.register(models.OpenAIAudioInteraction,OpenAIAudioAdmin)
admin.site.register(models.OpenAIImageInteraction,OpenAIImageAdmin)
admin.site.register(models.AIToolsModel)
