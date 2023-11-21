from django.contrib import admin
from . import models

admin.site.register(models.OpenAIChatInteraction)
admin.site.register(models.OpenAIAudioInteraction)
admin.site.register(models.OpenAIImageInteraction)
