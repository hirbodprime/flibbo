from django.urls import path
from .views import (
    FollowersModelListView,
    FollowModelCreateView,
    FollowModelRetrieveView,
    UnFollowModelCreateView,
    FollowingModelListView,
    FollowersModelUsersListView,
    FollowingModelUserListView,
    RequestToFollowCreateAPIView,
    RequestToFollowUpdateAPIView
)

urlpatterns = [
    path('followers/user/<int:id>/', FollowersModelUsersListView.as_view(), name='followers-user-list'),
    path('following/user/<int:id>/', FollowingModelUserListView.as_view(), name='following-user-list'),
    
    path('update-follow-request/<int:pk>/', RequestToFollowUpdateAPIView.as_view(), name='update-follow-request'),
    path('request-to-follow/', RequestToFollowCreateAPIView.as_view(), name='request-to-follow-list-create'),
    path('followers/', FollowersModelListView.as_view(), name='followers-list'),
    path('following/', FollowingModelListView.as_view(), name='following-list'),
    path('follow/<int:id>/', FollowModelCreateView.as_view(), name='follow-create'),
    path('follower/<int:id>/', FollowModelRetrieveView.as_view(), name='follower'),
    path('unfollow/<int:id>/', UnFollowModelCreateView.as_view(), name='unfollower'),
]
