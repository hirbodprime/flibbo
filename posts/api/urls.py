from django.urls import path , include
from . import views as custom_views



urlpatterns = [
    # URLs for Post
    # path('home/', include(router.urls)),
    path('followings-posts/', custom_views.FollowerPostsViewSet.as_view(), name='user-followers-posts'),
    path('favorite-categories/', custom_views.CategoryPostsViewSet.as_view(), name='user-favorite-categories-posts'),
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
    # path('tweet/reply-comments/', custom_views.TweetReplyCommentListView.as_view(), name='tweet-reply-comment-list'),
    path('tweet/reply-comments/<int:id>/', custom_views.TweetPostReplyCommentListView.as_view(), name='tweet-reply-comment-list'),
    path('tweet/reply-comment/create/<int:id>/', custom_views.TweetReplyCommentCreateView.as_view(), name='tweet-reply-comment-create'),


    # book urls

    path('books/list/', custom_views.BookPostListAPIView.as_view(), name='book_list'),
    path('book/create/', custom_views.BookPostCreateAPIView.as_view(), name='book_create'),
    path('book/get/<int:pk>/', custom_views.BookPostRetrieveAPIView.as_view(), name='book_detail'),
    path('book/update/<int:pk>/', custom_views.BookPostUpdateAPIView.as_view(), name='book_update'),
    path('book/delete/<int:pk>/', custom_views.BookPostDestroyAPIView.as_view(), name='book_delete'),

    path('book/save/<int:post_id>/', custom_views.book_save_post, name='book_save_post'),
    path('book/unsave/<int:post_id>/', custom_views.book_unsave_post, name='book_unsave_post'),
    path('book/like/<int:post_id>/', custom_views.book_like_post, name='book_like_post'),
    path('book/share/<int:pk>/', custom_views.ShareBookView.as_view(), name='book_share_post'),
    path('book/unlike/<int:post_id>/', custom_views.book_unlink_post, name='book_unlink_post'),

    path('book/comment/like/<int:comment_id>/', custom_views.book_like_comment, name='book_like_comment'),
    path('book/comment/unlike/<int:comment_id>/', custom_views.book_unlink_comment, name='book_unlink_comment'),
    path('book/reply-comment/like/<int:comment_id>/', custom_views.book_like_reply_comment, name='book_like_reply_comment'),
    path('book/reply-comment/unlike/<int:comment_id>/', custom_views.book_unlink_reply_comment, name='book_unlink_reply_comment'),

    path('book/comments/', custom_views.BookCommentListView.as_view(), name='book-comment-list'),
    path('book/comment/create/<int:id>/', custom_views.BookCommentCreateView.as_view(), name='book-comment-create'),
    path('book/reply-comments/', custom_views.BookReplyCommentListView.as_view(), name='book-reply-comment-list'),
    path('book/reply-comment/create/<int:id>/', custom_views.BookReplyCommentCreateView.as_view(), name='book-reply-comment-create'),

    # podcast urls

    path('podcasts/list/', custom_views.PodcastPostListAPIView.as_view(), name='podcast_list'),
    path('podcast/create/', custom_views.PodcastPostCreateAPIView.as_view(), name='podcast_create'),
    path('podcast/get/<int:pk>/', custom_views.PodcastPostRetrieveAPIView.as_view(), name='podcast_detail'),
    path('podcast/update/<int:pk>/', custom_views.PodcastPostUpdateAPIView.as_view(), name='podcast_update'),
    path('podcast/delete/<int:pk>/', custom_views.PodcastPostDestroyAPIView.as_view(), name='podcast_delete'),
    path('podcast/update/views/<str:ids>/', custom_views.PodcastPostUpdateViewsAPIView.as_view(), name='podcast_update_views'),


    path('podcast/save/<int:post_id>/', custom_views.podcast_save_post, name='podcast_save_post'),
    path('podcast/unsave/<int:post_id>/', custom_views.podcast_unsave_post, name='podcast_unsave_post'),
        path('podcast/view/<int:post_id>/', custom_views.podcast_view_post_api, name='podcast_view_post'),
    path('podcast/unlikes/<str:post_id>/', custom_views.podcast_unlikes_update, name='podcast_unlikes_post'),
    path('podcast/notifs/<str:post_id>/', custom_views.podcast_send_notification, name='podcast_unlikes_post'),
    path('podcast/like/<int:post_id>/', custom_views.podcast_like_post, name='podcast_like_post'),
    path('podcast/share/<int:pk>/', custom_views.SharePodcastView.as_view(), name='podcast_share_post'),
    path('podcast/unlike/<int:post_id>/', custom_views.podcast_unlink_post, name='podcast_unlink_post'),
    
    path('podcast/comment/like/<int:comment_id>/', custom_views.podcast_like_comment, name='podcast_like_comment'),
    path('podcast/comment/unlike/<int:comment_id>/', custom_views.podcast_unlink_comment, name='podcast_unlink_comment'),
    path('podcast/reply-comment/like/<int:comment_id>/', custom_views.podcast_like_reply_comment, name='podcast_like_reply_comment'),
    path('podcast/reply-comment/unlike/<int:comment_id>/', custom_views.podcast_unlink_reply_comment, name='podcast_unlink_reply_comment'),\

    path('podcast/comments/', custom_views.PodcastCommentListView.as_view(), name='podcast-comment-list'),
    path('podcast/comment/create/<int:id>/', custom_views.PodcastCommentCreateView.as_view(), name='podcast-comment-create'),
    path('podcast/reply-comments/', custom_views.PodcastReplyCommentListView.as_view(), name='podcast-reply-comment-list'),
    path('podcast/reply-comment/create/<int:id>/', custom_views.PodcastReplyCommentCreateView.as_view(), name='podcast-reply-comment-create'),
    # Add other URL patterns as needed
] 
