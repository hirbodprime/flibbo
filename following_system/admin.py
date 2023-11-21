from django.contrib import admin
from .models import FollowModel, RequestToFollow

# Admin class for FollowModel
class FollowModelAdmin(admin.ModelAdmin):
    list_display = ('user',)
# Register the admin class
admin.site.register(FollowModel,FollowModelAdmin)
admin.site.register(RequestToFollow)
