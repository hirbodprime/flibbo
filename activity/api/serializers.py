from rest_framework import serializers
from activity.models import Activity
from django.core.exceptions import ObjectDoesNotExist
from following_system.models import FollowModel, RequestToFollow
from django.conf import settings
from posts.api.serializers import TweetPostSerializer

from posts.models import TweetPostModel
from posts.api.serializers import TweetPostImageSerializer
class TweetSignleActivityPostSerializer(serializers.ModelSerializer):
    media = TweetPostImageSerializer(source='tweetpostimagesmodel_set', many=True, read_only=True)
    photo = serializers.SerializerMethodField()
    video  = serializers.SerializerMethodField()

    def get_video(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.video:
            # Get the full URL for the photo by prepending the domain
            site_domain_stream = f"{settings.SITE_DOMAIN}/posts/api/stream-video/"  # Replace this with your actual website domain
            return f"{site_domain_stream}{obj.id}"
        else:
            return None

    def get_photo(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.photo:
            # Get the full URL for the photo by prepending the domain
            return f"{settings.SITE_DOMAIN}{obj.photo.url}"
        else:
            return None
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = TweetPostModel
        fields = ['media','link','cover','id', 'photo_blur_hash','caption', 'voice','photo','video',]



class ActivitySerializer(serializers.ModelSerializer):
    profile_image_url  = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    def get_user_followed(self, obj):
        request_user = self.context['request'].user

        try:
            follow_model_obj = FollowModel.objects.get(user=obj.user)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False
        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    
    def get_request_status(self,obj):
        request_user = self.context['request'].user
        status = None
        try:
            request_follow_obj = RequestToFollow.objects.get(
                requset_reciever=obj.user,  # The user who will receive the request
                request_sender=request_user   # The user who sent the request
            )
        except RequestToFollow.DoesNotExist:
            request_follow_obj = None

        if not request_follow_obj is None:
            status = request_follow_obj.status
        return status
    def get_private(self, obj):
        return obj.user.private
    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_user_username(self, obj):
        return obj.user.username 
    def get_user_id(self, obj):
        return obj.user.id 
    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    class Meta:
        model = Activity
        fields = ['user_followed','request_status','private','user_id','user_username','user_full_name','profile_image_url','activity_type','created_at','tweet','followed_user']



class ActivitySerializerV2(serializers.ModelSerializer):
    tweet_details = serializers.SerializerMethodField()
    profile_image_url  = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    comment_text = serializers.SerializerMethodField()

    def get_comment_text(self, obj):
        # If the activity is related to a comment, return the comment's text
        if obj.activity_type in 'comment' and obj.tweet_comment:
            print(obj.tweet_comment.text)
            return obj.tweet_comment.text
        return None
    def get_tweet_details(self, obj):
        request = self.context['request']
        if obj.tweet:
            return TweetSignleActivityPostSerializer(obj.tweet,context={'request':request}).data
        return None
    def get_user_followed(self, obj):
        request_user = self.context['request'].user

        try:
            follow_model_obj = FollowModel.objects.get(user=obj.user)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False
        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    
    def get_request_status(self,obj):
        request_user = self.context['request'].user
        status = None
        try:
            request_follow_obj = RequestToFollow.objects.get(
                requset_reciever=obj.user,  # The user who will receive the request
                request_sender=request_user   # The user who sent the request
            )
        except RequestToFollow.DoesNotExist:
            request_follow_obj = None

        if not request_follow_obj is None:
            status = request_follow_obj.status
        return status
    def get_private(self, obj):
        return obj.user.private
    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_user_username(self, obj):
        return obj.user.username 
    def get_user_id(self, obj):
        return obj.user.id 
    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    class Meta:
        model = Activity
        fields = ['comment_text','user_followed','request_status','private','user_id','tweet_details','user_username','user_full_name','profile_image_url','activity_type','created_at','tweet','followed_user']




