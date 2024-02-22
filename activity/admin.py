from django.contrib import admin
from .models import Activity

class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'activity_type', 'tweet', 'followed_user', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'tweet__content')  # Replace 'username' and 'content' with actual field names if necessary

admin.site.register(Activity, ActivityAdmin)

