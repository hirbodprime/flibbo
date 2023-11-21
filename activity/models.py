from django.db import models
from posts.models import TweetPostModel , TweetCommentModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Activity(models.Model):
    VIEW = 'view'
    LIKE = 'like'
    UNLIKE = 'unlike'
    SAVE = 'save'
    UNSAVE = 'unsave'
    FOLLOW = 'follow'
    UNFOLLOW = 'unfollow'
    COMMENT = 'comment'
    UNCOMMENT = 'uncomment'
    ACTIVITY_CHOICES = (
        (VIEW, 'View'),
        (LIKE, 'Like'),
        (SAVE, 'Save'),
        (UNSAVE, 'UnSave'),
        (FOLLOW, 'Follow'),
        (UNFOLLOW, 'UnFollow'),
        (COMMENT, 'Comment'),
        (UNCOMMENT, 'UnComment'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey(TweetPostModel, on_delete=models.CASCADE, null=True, blank=True)
    tweet_comment = models.ForeignKey(TweetCommentModel, on_delete=models.CASCADE, null=True, blank=True)
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_user', null=True, blank=True)
    activity_type = models.CharField(max_length=12, choices=ACTIVITY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

