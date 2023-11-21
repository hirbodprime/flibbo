from django.contrib import admin
from .models import (TweetPostModel,BookPostModel,PodcastPostModel,TweetCommentModel, TweetReplyCommentModel,
    PodcastCommentModel, PodcastReplyCommentModel,
    BookCommentModel, BookReplyCommentModel,ReportPost)  # Import the concrete model

admin.site.register(ReportPost)


# Admin class for TweetPostModel
class TweetPostModelAdmin(admin.ModelAdmin):
    list_display = ('id','cover','video','total_comments','title', 'user', 'created_date', 'updated_date', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'user__username', 'caption','viewed_by_users','total_views')
    # prepopulated_fields = {'slug': ('id',)}

# Register the admin class for TweetPostModel
admin.site.register(TweetPostModel, TweetPostModelAdmin)


class BookPostModelAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'user', 'created_date', 'updated_date', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'user__username', 'caption','viewed_by_users','total_views')
    prepopulated_fields = {'slug': ('title',)}

# Register the admin class for BookPostModel
admin.site.register(BookPostModel, BookPostModelAdmin)


class PodcastPostModelAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'user', 'created_date', 'updated_date', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'user__username', 'caption','viewed_by_users','total_views')
    prepopulated_fields = {'slug': ('title',)}

# Register the admin class for PodcastPostModel
admin.site.register(PodcastPostModel, PodcastPostModelAdmin)




@admin.register(TweetCommentModel)
class TweetCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'post')

@admin.register(TweetReplyCommentModel)
class TweetReplyCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'parent_comment')

@admin.register(PodcastCommentModel)
class PodcastCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'post')

@admin.register(PodcastReplyCommentModel)
class PodcastReplyCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'parent_comment')

@admin.register(BookCommentModel)
class BookCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'post')

@admin.register(BookReplyCommentModel)
class BookReplyCommentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'text', 'created_at', 'parent_comment')
