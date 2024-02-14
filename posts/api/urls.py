from django.urls import path , include
from . import views as custom_views
from posts.partial_videos import serve_video

urlpatterns = [
    # URLs for Post
    path('stream-video/<int:post_id>/', serve_video, name='stream-video'),
    # path('home/', include(router.urls)),
    path('followings-posts/', custom_views.FollowerPostsViewSet.as_view(), name='user-followers-posts'),
    path('favorite-categories/', custom_views.CategoryPostsViewSet.as_view(), name='user-favorite-categories-posts'), # home api
    path('tweet-post-sizes/<int:tweet_post_id>/', custom_views.get_photo_sizes, name='get_photo_sizes'),
    # tweet urls
    path('tweet/likes/list/<int:post_id>/', custom_views.TweetPostLikedListApiView.as_view(), name='tweet-post-like-list'),
    path('tweet/views/list/<int:post_id>/', custom_views.TweetPostViewedListApiView.as_view(), name='tweet-post-like-list'),
    
    path('tweet/comment/report/<int:comment_id>/', custom_views.ReportCommentView.as_view(), name='report-comment'),
    path('tweet/report/<int:post_id>/', custom_views.ReportPostCreateApiView.as_view(), name='report-user'),
    path('tweets/photo-video/list/<int:user_id>/', custom_views.TweetPostListAPIView.as_view(), name='tweet_photo_image_list'),
    path('tweets/text/list/<int:user_id>/', custom_views.TweetPostTextListAPIView.as_view(), name='tweet_text_list'),
    path('tweet/create/', custom_views.TweetPostCreateAPIView.as_view(), name='tweet_create'),
    path('tweet/get/<int:pk>/', custom_views.SingleTweetPostAPIView.as_view(), name='tweet_detail'),
    path('tweet/update/<int:pk>/', custom_views.TweetPostUpdateAPIView.as_view(), name='tweet_update'),
    path('tweet/delete/<int:pk>/', custom_views.TweetPostDestroyAPIView.as_view(), name='tweet_delete'),
    
    path('tweets/update/views/<str:ids>/', custom_views.TweetPostUpdateViewsAPIView.as_view(), name='tweets_update_views'),
    path('tweets/update/saves/<str:ids>/', custom_views.TweetPostUpdateSavesAPIView.as_view(), name='tweets_update_saves'),
    path('tweets/update/likes/<str:ids>/', custom_views.TweetPostUpdateLikesAPIView.as_view(), name='tweets_update_likes'),
    path('tweets/update/unlikes/<str:ids>/', custom_views.TweetPostUpdateUnLikesAPIView.as_view(), name='tweets_update_unlikes'),
    path('tweets/update/unsaves/<str:ids>/', custom_views.TweetPostUpdateUnSavesAPIView.as_view(), name='tweets_update_unsaves'),
    
    path('tweet/save/<int:post_id>/', custom_views.tweet_save_post, name='tweet_save_post'),
    path('tweet/unsave/<int:post_id>/', custom_views.tweet_unsave_post, name='tweet_unsave_post'),
    path('tweet/like/<int:post_id>/', custom_views.tweet_like_post, name='tweet_like_post'),
    path('tweet/share/<int:pk>/', custom_views.ShareTweetView.as_view(), name='tweet_share_post'),
    path('tweet/unlike/<int:post_id>/', custom_views.tweet_unlink_post, name='tweet_unlink_post'),
    
    path('tweet/comment/delete/<int:pk>/', custom_views.DeleteTweetCommentView.as_view(), name='delete-comment-tweet'),
    path('tweet/comment/like/<str:ids>/', custom_views.TweetPostCommentUpdateLikesAPIView.as_view(), name='tweet_like_comment'),
    path('tweet/comment/unlike/<str:ids>/', custom_views.TweetPostUpdateCommentUnLikesAPIView.as_view(), name='tweet_unlink_comment'),
    path('tweet/reply-comment/like/<int:comment_id>/', custom_views.tweet_like_reply_comment, name='tweet_like_reply_comment'),
    path('tweet/reply-comment/unlike/<int:comment_id>/', custom_views.tweet_unlink_reply_comment, name='tweet_unlink_reply_comment'),

    # path('tweet/comments/', custom_views.TweetCommentListView.as_view(), name='tweet-comment-list'),
    path('tweet/comments/<int:tweet_id>/', custom_views.TweetPostCommentListView.as_view(), name='tweet-comment-list-post'),
    path('tweet/comment/create/<int:id>/', custom_views.TweetCommentCreateView.as_view(), name='tweet-comment-create'),
    path('tweet/pin-comment/<int:comment_id>/', custom_views.PinCommentView.as_view(), name='pin-comment'),
    path('tweet/comment/hide/<int:comment_id>/', custom_views.HideCommentView.as_view(), name='hide-comment'),

    # path('tweet/reply-comments/', custom_views.TweetReplyCommentListView.as_view(), name='tweet-reply-comment-list'),
    path('tweet/reply-comments/<int:id>/', custom_views.TweetPostReplyCommentListView.as_view(), name='tweet-reply-comment-list'),
    path('tweet/reply-comment/create/<int:id>/', custom_views.TweetReplyCommentCreateView.as_view(), name='tweet-reply-comment-create'),


    # book urls

    path('books/list/', custom_views.BookListView.as_view(), name='book_list'),
    path('books/<int:book_id>/pages/', custom_views.BookPagesView.as_view(), name='book-pages'),


] 
