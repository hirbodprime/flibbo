from django.contrib import admin
from django.contrib.admin import AdminSite , ModelAdmin
from .models import (TweetPostModel,BookPostModel,PodcastPostModel,TweetCommentModel, TweetReplyCommentModel,
    PodcastCommentModel, PodcastReplyCommentModel,
    BookCommentModel, BookReplyCommentModel,ReportPost,Language,Book,Page,UserBookProgress)  # Import the concrete model

admin.site.register(ReportPost)

class BookAdmin(AdminSite):
    site_header = 'book admin'
    site_title = 'book admin'



book_admin = BookAdmin(name='bookadmin')
book_admin.register(Language, ModelAdmin)
book_admin.register(Book, ModelAdmin)
book_admin.register(Page, ModelAdmin)
book_admin.register(UserBookProgress, ModelAdmin)



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
