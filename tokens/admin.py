from django.contrib import admin
from .models import TokenModel

class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'refresh_token')
    list_filter = ('user',)

admin.site.register(TokenModel, TokenAdmin)
