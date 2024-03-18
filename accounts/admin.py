from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OldUsername, SavedByUser, ReportUser, AccessToken, BlockModel, ChangeUsernameModel, ProfileImagesModel,LanguageModel, JobModel, InterestsModel, HabitsModel, AboutMeModel  # Ensure correct spelling for your models

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
        ('Personal Info', {'fields': ('username', 'bonus_code','full_name', 'birthday','profile_image','country','private','premium')}),
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





@admin.register(LanguageModel)
class LanguageModelAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Adjust this to display fields you're interested in
    search_fields = ('name',)  # Add fields here you want to be searchable

@admin.register(JobModel)
class JobModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'education', 'user')  # Customize as needed
    list_filter = ('company', 'education')  # Filters on the side panel
    search_fields = ('title', 'company', 'education', 'user__username')  # Adjust according to your user model's fields

@admin.register(InterestsModel)
class InterestsModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')

@admin.register(HabitsModel)
class HabitsModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')

@admin.register(AboutMeModel)  # Ensure this matches the exact class name of your model
class AboutMeModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'height', 'star_sign')
    search_fields = ('user__username', 'star_sign')
