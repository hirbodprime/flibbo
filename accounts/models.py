from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from accounts.managers import CustomUserManager
from django.conf import settings
from django.utils import timezone
from posts.utils.upload_image import ProfileUploadHandler 


upload_profile_image_handler = ProfileUploadHandler('profile_image', 'profile_image', 'profile_images')

def upload_profile_image(instance, filename):
    return upload_profile_image_handler.get_filename(instance, filename)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)  # Add username field 
    full_name = models.CharField(max_length=60,null=True,blank=True)
    bonus_code = models.CharField(max_length=8,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    join_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    birthday = models.DateField(null=True, blank=True)
    last_username_change = models.DateTimeField(null=True, blank=True)
    bio = models.CharField(max_length=100, blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True) 
    profile_image = models.ImageField(upload_to=upload_profile_image,blank=True, null=True) 
    private = models.BooleanField(default=False)
    objects = CustomUserManager()
    premium = models.BooleanField(default=False)
    followers_count = models.BigIntegerField(default=0)
    followings_count = models.BigIntegerField(default=0)
    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']  # Add username to REQUIRED_FIELDS
    # Other methods and __str__ definition
    def __str__(self):
        return self.email

    def increment_followers_count(self):
        print('method increment_followers_count called')
        self.followers_count += 1
        self.save()

        # self.save(update_fields=['followers_count'])
    
    def decrement_followers_count(self):
        print('method decrement_followers_count called')
        self.followers_count -= 1

        # self.save(update_fields=['followers_count'])
        self.save()
    
    def increment_followings_count(self):
        print('method increment_followings_count called')
        self.followings_count += 1
        
        self.save()
        # self.save(update_fields=['followings_count'])
    
    def decrement_followings_count(self):
        print('method decrement_followings_count called')
        self.followings_count -= 1
        
        self.save()
        # self.save(update_fields=['followings_count'])
    
    def set_private(self, is_private):
        self.private = is_private
        self.save()

    def is_profile_private(self):
        return self.private
    

class ProfileImagesModel(models.Model):
    pass

class OldUsername(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    old_username = models.CharField(max_length=30)
    expiration_date = models.DateTimeField()
    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = timezone.now() + timezone.timedelta(days=15)
        super().save(*args, **kwargs)


from posts.models import (BasePostModel,TweetPostModel,BookPostModel,PodcastPostModel)
from marketplace.models import NftProductModel
from django.contrib.auth import get_user_model
User = get_user_model()

from datetime import datetime

report_reasons_choices = (
    ("spam","spam"),
    ("nudity","nudity"),
    ("self-harm","self-harm"),
    ("dangers-goods","dangers-goods"),
    ("misinformation","misinformation"),
    ("graphic-violence","graphic-violence"),
    ("privacy-violation","privacy-violation"),
    ("hateful-activities","hateful-activities"),
    ("harassment-criticism","harassment-criticism"),
    ("my-intellectual-property","my-intellectual-property"),
    )

from datetime import datetime

class ReportUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_by = models.ManyToManyField(User, related_name='reported_by', blank=True)
    unban_time = models.DateTimeField(null=True, blank=True)  # Nullable DateTimeField
    report_count = models.BigIntegerField(default=0)
    report_reasons = models.CharField(max_length=100,choices=report_reasons_choices,null=True, blank=True)
    def reports_count(self):
        return self.report_count
    
class SavedByUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    # user_tweets = models.ManyToManyField(TweetPostModel, related_name='user_tweets', blank=True)
    saved_tweets = models.ManyToManyField(TweetPostModel, related_name='tweet_posts_saved', blank=True)
    
    # user_books = models.ManyToManyField(BookPostModel, related_name='user_books', blank=True)
    saved_books = models.ManyToManyField(BookPostModel, related_name='book_posts_saved', blank=True)
    
    # user_podcasts = models.ManyToManyField(PodcastPostModel, related_name='user_podcasts', blank=True)
    saved_podcasts = models.ManyToManyField(PodcastPostModel, related_name='podcast_posts_saved', blank=True)
    
    nfts_bought = models.ManyToManyField(NftProductModel, related_name='nfts_bought', blank=True)
    
    
    
    

class AccessToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return f'{self.user}'


class BlockModel(models.Model):
    user = models.ForeignKey(User, related_name='user_blocking', on_delete=models.CASCADE)
    blocked_users = models.ManyToManyField(User, related_name='users_blocked', blank=True)
    blocked_by = models.ManyToManyField(User, related_name='blocked_by_users', blank=True)
    def __str__(self):
        return f"{self.user.username} has blocked {self.blocked_users.count()} user(s)"
        
        
        
        
class ChangeUsernameModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)
    username = models.CharField(max_length=250, unique=True)
    started_at = models.DateTimeField(blank=True, null=True, default=None)
    ended_at = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.username

