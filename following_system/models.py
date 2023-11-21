from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following_users', blank=True)
    following = models.ManyToManyField(User, related_name='followers_users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_user_following(self, user_to_check):
        """
        Check if the user associated with this FollowModel is following another user.
        """
        following_ids = self.following.values_list('id', flat=True)
        return user_to_check.id in following_ids
        
    def follow(self, user_to_follow):
        """
        Method to follow another user.
        """
        if user_to_follow != self.user:

            self.following.add(user_to_follow)
            user_to_follow_follow_model, created = FollowModel.objects.get_or_create(user=user_to_follow)
            user_to_follow_follow_model.followers.add(self.user)
            
    def unfollow(self, user_to_unfollow):
        """
        Method to unfollow a user.
        """
        self.following.remove(user_to_unfollow)
        user_to_follow_follow_model, created = FollowModel.objects.get_or_create(user=user_to_unfollow)
        user_to_follow_follow_model.followers.remove(self.user)

    def is_following(self, user):
        """
        Check if this user is following another user.
        """
        if  user in self.following.all():
            return False
        else:
            return True

    def is_followed_by(self, user):
        """
        Check if this user is followed by another user.
        """
        return user in self.followers.all()

    def followers_count(self):
        """
        Get the count of followers for this user.
        """
        return self.followers.count()

    def following_count(self):
        """
        Get the count of users this user is following.
        """
        return self.following.count()
        
        



status_choices = (
    ('ACCEPTED','ACCEPTED'),
    ('REJECTED','REJECTED'),
    ('PENDING','PENDING'),

    )
class RequestToFollow(models.Model):
    request_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sending_request')
    requset_reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_the_user')
    status = models.CharField(choices=status_choices,default='PENDING') 
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)