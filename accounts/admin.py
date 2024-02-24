from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OldUsername, SavedByUser, ReportUser, AccessToken, BlockModel, ChangeUsernameModel, ProfileImagesModel
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.html import format_html  # Import format_html

admin.site.register(ChangeUsernameModel)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('id', 'join_date','email', 'username', 'full_name', 'is_active', 'is_staff','followers_count','followings_count')
    list_filter = ('is_active', 'is_staff', 'birthday','followers_count','followings_count')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'bonus_code','full_name', 'birthday','profile_image','country','private')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions','followers_count','followings_count')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'birthday', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('join_date',)
    actions = ['view_tokens']

    def view_tokens(self, request, queryset):
        for user in queryset:
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            refresh_token_str = str(refresh_token)
            self.message_user(request, format_html(f"User: {user.username}<br>Access Token: {access_token}<br>Refresh Token: {refresh_token_str}"))

    view_tokens.short_description = "View Tokens for Selected Users"

admin.site.register(CustomUser, CustomUserAdmin)

    
# admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BlockModel)
admin.site.register(ProfileImagesModel)
admin.site.register(ReportUser)
admin.site.register(OldUsername)
admin.site.register(SavedByUser)
admin.site.register(AccessToken)