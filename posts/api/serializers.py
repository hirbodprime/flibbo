from rest_framework import serializers
from posts.models import (
    TweetPostModel, BookPostModel, PodcastPostModel,TweetCommentModel,
    TweetReplyCommentModel, PodcastCommentModel, PodcastReplyCommentModel,
    BookCommentModel, BookReplyCommentModel,ReportPost,Book,Page, TweetPostImagesModel,TweetPostImagesModel,MentionsUsersModel
)
from django.shortcuts import get_object_or_404
from accounts.models import CustomUser
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from following_system.models import FollowModel, RequestToFollow
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import BlockModel
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class TweetPostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetPostImagesModel
        fields = ['image', 'video', 'created_at',"photo_blur_hash_video", "cover_video", "photo_blur_hash_image", "cover_image"]  
    
    def to_representation(self, instance):
        # Call the base implementation first to get the usual serialization
        ret = super().to_representation(instance)
        # Add the 'type' field based on whether it's an image or video
        ret['type'] = instance.media_type
        return ret


import blurhash
from PIL import Image


def generate_blurhash(image_file):
    with Image.open(image_file) as image:
        image.thumbnail((100, 100), Image.Resampling.LANCZOS)
        image = image.convert("RGB")
        blurhashe = blurhash.encode(image, x_components=4, y_components=3)
        print(blurhashe)
        return blurhashe

class TweetPostCreateV2Serializer(serializers.ModelSerializer):
    videos = serializers.ListField(child=serializers.FileField(),write_only=True, required=False)
    # photo_blur_hash_video = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    cover_video = serializers.ListField(child=serializers.FileField(),write_only=True,  required=False)
    
    images = serializers.ListField(child=serializers.ImageField(),write_only=True, required=False)
    # photo_blur_hash_image = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    cover_image = serializers.ListField(child=serializers.FileField(),write_only=True, required=False)
    
    tag_users = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    offset_X = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    offset_y = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    index = serializers.ListField(child=serializers.CharField(),write_only=True, required=False)
    
    class Meta:
        model = TweetPostModel
        fields = ['aspect_ratio','tag_users','index','offset_X','offset_y','options','file','link','id', 'title', 'height', 'caption', 'hashtag', 'location', 'category', 'urls', 'voice', 'photo', 'video', 'images','videos', 'cover_video', 'cover_image']

    def create(self, validated_data):
        # Pop media-related fields from validated_data
        videos_data = validated_data.pop('videos', [])
        # photo_blur_hash_video_data = validated_data.pop('photo_blur_hash_video', [])
        cover_video_data = validated_data.pop('cover_video', [])

        images_data = validated_data.pop('images', [])
        # photo_blur_hash_image_data = validated_data.pop('photo_blur_hash_image', [])
        cover_image_data = validated_data.pop('cover_image', [])
        tag_users_data = validated_data.pop('tag_users', [])
        offset_x_data = validated_data.pop('offset_X', [])  # Adjust to the correct field name
        offset_y_data = validated_data.pop('offset_y', [])  # Adjust to the correct field name    
        index_data = validated_data.pop('index', [])  # Adjust to the correct field name    
        # Create the TweetPostModel instance
        tweet = TweetPostModel.objects.create(**validated_data)
        for cover_image_file in cover_image_data:
            cover_image_blurhash = generate_blurhash(cover_image_file)
            # Save your TweetPostImagesModel instance including the cover_image_blurhash

        for cover_video_file in cover_video_data:
            cover_video_blurhash = generate_blurhash(cover_video_file)

        # Before creating objects for videos
        if videos_data:
            for i, video_data in enumerate(videos_data):
                # This should be creating video objects, not image objects.
                TweetPostImagesModel.objects.create(
                    tweet=tweet,
                    video=video_data,
                    # photo_blur_hash_video=photo_blur_hash_video_data[i] if i < len(photo_blur_hash_video_data) else '',
                    photo_blur_hash_video=cover_video_blurhash,
                    cover_video=cover_video_data[i] if i < len(cover_video_data) else None
                )

        # Associate videos with the tweet
        for i in range(len(images_data)):
        
            TweetPostImagesModel.objects.create(
                tweet=tweet,
                image=images_data[i],
                # photo_blur_hash_image=photo_blur_hash_image_data[i] if i < len(photo_blur_hash_image_data) else '',
                photo_blur_hash_video=cover_image_blurhash,
                cover_image=cover_image_data[i] if i < len(cover_image_data) else None
            )
        
        # Create MentionsUsersModel instances
        tag_users_data = []
        offset_x_data = []
        offset_y_data = []
        index_data = []
        # Extract indexed data from self.initial_data instead of validated_data
        for key in self.initial_data.keys():
            if 'tag_users' in key:
                index = key.split('[')[1].split(']')[0]  # Extract the index
                tag_users_data.append((index, self.initial_data[key]))
            elif 'offset_x' in key:
                index = key.split('[')[1].split(']')[0]
                offset_x_data.append((index, self.initial_data[key]))
            elif 'offset_y' in key:
                index = key.split('[')[1].split(']')[0]
                offset_y_data.append((index, self.initial_data[key]))
            elif 'index' in key:
                index = key.split('[')[1].split(']')[0]
                index_data.append((index, self.initial_data[key]))
        # Sort the data by index to ensure they match up
        tag_users_data.sort(key=lambda x: x[0])
        offset_x_data.sort(key=lambda x: x[0])
        offset_y_data.sort(key=lambda x: x[0])
        index_data.sort(key=lambda x: x[0])

        # Now you can iterate and create MentionsUsersModel instances
        for ((_, user_id), (_, x), (_, y), (_, i)) in zip(tag_users_data, offset_x_data, offset_y_data,index_data):
            try:
                # Check if the user exists before creating the MentionsUsersModel instance
                user = CustomUser.objects.get(id=user_id)
                MentionsUsersModel.objects.create(
                    user=user,
                    tweet=tweet,
                    offset_x=x,
                    offset_y=y,
                    index=i,
                )
            except ObjectDoesNotExist:
                # Handle the case where the user does not exist
                print(f"User with id {user_id} does not exist.")
            except ValueError:
                # Handle the case where x or y is not a valid integer
                print(f"Invalid value for offset_x or offset_y: {x}, {y}")
        
        return tweet




from accounts.api.serializers import CustomUserSerializerV2
# You will also need a serializer for the MentionsUsersModel
class MentionsUsersModelSerializer(serializers.ModelSerializer):
    user = CustomUserSerializerV2(read_only=True)  # Use the CustomUserSerializer for nested user data
    offset = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = MentionsUsersModel
        fields = ('user', 'offset','index')  # Update this line

    def get_offset(self, obj):
        # This method constructs the offset object
        return {
            'x': obj.offset_x,
            'y': obj.offset_y,
        }

        
class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'book', 'language', 'page_number', 'content']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'cover_image']

class TweetSignlePostSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    profile_image_url  = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    mention_users = serializers.SerializerMethodField()
    video  = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    user_saved = serializers.SerializerMethodField()
    # share_post = serializers.SerializerMethodField()
    user_viewed = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    def get_tags(self, obj):
        mentions = obj.mentionsusersmodel_set.all()
        return MentionsUsersModelSerializer(mentions, many=True).data
    def get_total_comments(self,obj):
        return TweetCommentModel.objects.filter(post=obj).count()
    def get_location(self,obj):
        if obj.location and obj.location != 'null':
            return obj.location
        else:
            return None

    def get_request_status(self,obj):
        request_user = self.context['request'].user
        status = None
        try:
            print(request_user, obj.user)
            request_follow_obj = RequestToFollow.objects.get(
                requset_reciever=obj.user,  # The user who will receive the request
                request_sender=request_user   # The user who sent the request
            )
        except RequestToFollow.DoesNotExist:
            request_follow_obj = None

        if not request_follow_obj is None:
            status = request_follow_obj.status
        return status

    def get_private(self,obj):
        return obj.user.private
    # def get_location(self,obj):
    #     return obj.user.country
    def get_user_followed(self, obj):
        request_user = self.context['request'].user

        try:
            follow_model_obj = FollowModel.objects.get(user=obj.user)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False

        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    def get_likes(self, obj):
        request_user = self.context['request'].user

        block_obj,created = BlockModel.objects.get_or_create(user=request_user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=request_user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        if request_user.is_authenticated:
            # Get the first 3 likes for the post
            first_3_likes = list(obj.likes.exclude(id__in=blocked_users_combined).all().values('id', 'username', 'profile_image'))
            # Prepend site_domain to profile image URL
            for like in first_3_likes:
                if 'profile_image' in like and like['profile_image']:
                    like['profile_image'] = f"{settings.SITE_DOMAIN}/media/{like['profile_image']}"
                else:
                    like['profile_image'] = None
            return  first_3_likes

    def get_comments(self, obj):
        return []

    def get_user_viewed(self, obj):
        # Get the current request user
        request_user = self.context['request'].user
        if request_user.is_authenticated:
            return obj.viewed_by_users.filter(email=request_user).exists()
        return False

    def get_user_saved(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.saved_by_users.filter(email=request_user).exists()
        return False
    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_mention_users(self, obj):
        return [mention_user.username for mention_user in obj.mention_users.all()]


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

    def get_user_username(self, obj):
        return obj.user.username 

    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    # def get_share_post(self, obj):
    #     # You can generate the share link based on your project's URL structure
    #     link = obj.get_absolute_url(obj.id)
    #     return link
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = TweetPostModel
        fields = ['aspect_ratio','cover','private','request_status','user_followed','likes','comments','id', 'photo_blur_hash','height','user','user_username','user_liked','user_saved','user_viewed' ,'profile_image_url','user_full_name','title', 'caption', 'hashtag', 'location','urls', 'category', 'created_date',
                'updated_date','photo','video',
                'total_views','total_shares','share_post','total_saves','total_comments','total_likes','mention_users','likes']



class UserSerializer(serializers.ModelSerializer):
    profile_image  = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    def get_user_followed(self, obj):
        request_user = self.context['request'].user

        try:
            follow_model_obj = FollowModel.objects.get(user=obj)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False
        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    
    def get_request_status(self,obj):
        request_user = self.context['request'].user
        status = None
        try:
            request_follow_obj = RequestToFollow.objects.get(
                requset_reciever=obj,  # The user who will receive the request
                request_sender=request_user   # The user who sent the request
            )
        except RequestToFollow.DoesNotExist:
            request_follow_obj = None

        if not request_follow_obj is None:
            status = request_follow_obj.status
        return status

    def get_profile_image(self, obj):
        profile_image_url = f"{settings.SITE_DOMAIN}{obj.profile_image.url}" if obj.profile_image else None
        return profile_image_url
    class Meta:
        model = User
        fields = ('request_status','user_followed','id', 'private','email', 'username', 'full_name', 'join_date', 'birthday','bio', 'followers_count','followings_count',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url','profile_image','country',)





class CustomCountryField(serializers.Field):
    def to_representation(self, obj):
        return str(obj)

    def to_internal_value(self, data):
        return data

class ReportPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportPost
        fields = ('id', 'post', 'reported_by')
        read_only_fields  = ('post', 'reported_by')

    def validate(self, data):
        """
        Custom validation to prevent duplicate reporting by the same user.
        """
        post = self.context['view'].kwargs.get('post_id')
        reported_by = self.context['request'].user
        print('adsfad2121312sf')

        already_reported = ReportPost.objects.filter(
            post_id=post,
            reported_by=reported_by
        ).exists()
        if already_reported:
            raise serializers.ValidationError({"message": "You have already reported this post"})

        return data

        
class TweetPostConsumerSerializer(serializers.ModelSerializer):
    # location = CustomCountryField()

    photo = serializers.SerializerMethodField()
    profile_image_url  = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    mention_users = serializers.SerializerMethodField()
    video  = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    user_saved = serializers.SerializerMethodField()
    # share_post = serializers.SerializerMethodField()
    
    user_viewed = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    def get_total_comments(self,obj):
        return TweetCommentModel.objects.filter(post=obj).count()
    def get_location(self,obj):
        if obj.location and obj.location != 'null':
            return obj.location
        else:
            return None

    def get_request_status(self,obj):
        request_user = self.context['request']
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

    def get_private(self,obj):
        return obj.user.private
    # def get_location(self,obj):
    #     return obj.user.country
    def get_user_followed(self, obj):
        request_user = self.context['request']

        try:
            follow_model_obj,created = FollowModel.objects.get_or_create(user=obj.user)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False

        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    def get_likes(self, obj):
        request_user = self.context['request']

        block_obj,created = BlockModel.objects.get_or_create(user=request_user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=request_user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        if request_user.is_authenticated:
            # Get the first 3 likes for the post
            first_3_likes = list(obj.likes.exclude(id__in=blocked_users_combined).all()[:3].values('id', 'username', 'profile_image'))
            for like in first_3_likes:
                if 'profile_image' in like and like['profile_image']:
                    like['profile_image'] = f"{settings.SITE_DOMAIN}/media/{like['profile_image']}"
                else:
                    like['profile_image'] = None
            return first_3_likes
            
    def get_comments(self, obj):
        return []
    def get_user_viewed(self, obj):
        # Get the current request user
        request_user = self.context['request']
        if request_user.is_authenticated:
            return obj.viewed_by_users.filter(email=request_user).exists()
        return False

    def get_user_saved(self, obj):
        # Get the current request user
        request_user = self.context['request']

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.saved_by_users.filter(email=request_user).exists()
        return False
    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request']

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_mention_users(self, obj):
        return [mention_user.username for mention_user in obj.mention_users.all()]


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

    def get_user_username(self, obj):
        return obj.user.username 

    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            # If request object is not available, construct the URL manually based on the site domain
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    # def get_share_post(self, obj):
    #     # You can generate the share link based on your project's URL structure
    #     link = obj.get_absolute_url(obj.id)
    #     return link
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = TweetPostModel
        fields = ['aspect_ratio','comments','cover','private','request_status','user_followed','likes','id', 'photo_blur_hash','height', 'user',
                'user_username','user_liked','user_saved','user_viewed' ,'profile_image_url','user_full_name','title',
                'caption', 'hashtag', 'location','urls', 'category', 'created_date',
                'updated_date','photo','video',
                'total_views','total_shares','share_post','total_saves','total_comments','total_likes','mention_users','likes']

               

        
class TweetPostSerializer(serializers.ModelSerializer):
    # location = CustomCountryField()
    media = TweetPostImageSerializer(source='tweetpostimagesmodel_set', many=True, read_only=True)
    photo = serializers.SerializerMethodField()
    profile_image_url  = serializers.SerializerMethodField()
    tags  = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    mention_users = serializers.SerializerMethodField()
    video  = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    user_saved = serializers.SerializerMethodField()
    premium = serializers.SerializerMethodField()
    # share_post = serializers.SerializerMethodField()
    
    user_viewed = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    # location = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    voice = serializers.SerializerMethodField()
    def get_tags(self, obj):
        mentions = obj.mentionsusersmodel_set.all()
        return MentionsUsersModelSerializer(mentions, many=True).data

    def get_premium(self,obj):
        return obj.user.premium
    def get_voice(self,obj):
        if obj.voice:
            return f"{settings.SITE_DOMAIN}{obj.voice.url}" 
        return None
    def get_file(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.file:
            # Get the full URL for the photo by prepending the domain
            return f"{settings.SITE_DOMAIN}{obj.file.url}"
        else:
            return None
    def get_link(self, obj):
        # Get the current request object
        request = self.context.get('request')

        # Check if the object has a 'photo' field
        if obj.link:
            # Get the full URL for the photo by prepending the domain
            return obj.link
        else:
            return None
    def get_total_comments(self,obj):
        return TweetCommentModel.objects.filter(post=obj).count()
    def get_location(self,obj):
        if obj.location and obj.location != 'null':
            return obj.location
        else:
            return None

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

    def get_private(self,obj):
        return obj.user.private
    # def get_location(self,obj):
    #     return obj.user.country
    def get_user_followed(self, obj):
        request_user = self.context['request'].user

        try:
            follow_model_obj,created = FollowModel.objects.get_or_create(user=obj.user)  # Get the FollowModel instance for the user in the object
        except ObjectDoesNotExist:
            return False

        is_followed = follow_model_obj.is_followed_by(request_user)  # Use the is_followed_by method to check if the request_user is following obj.user

        return is_followed
    def get_likes(self, obj):
        request_user = self.context['request'].user

        block_obj,created = BlockModel.objects.get_or_create(user=request_user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=request_user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        if request_user.is_authenticated:
            # Get the first 3 likes for the post
            first_3_likes = list(obj.likes.exclude(id__in=blocked_users_combined).all()[:3].values('id', 'username', 'profile_image'))
            for like in first_3_likes:
                if 'profile_image' in like and like['profile_image']:
                    like['profile_image'] = f"{settings.SITE_DOMAIN}/media/{like['profile_image']}"
                else:
                    like['profile_image'] = None
            return first_3_likes
            
    def get_comments(self, obj):
        return []
    def get_user_viewed(self, obj):
        # Get the current request user
        request_user = self.context['request'].user
        if request_user.is_authenticated:
            return obj.viewed_by_users.filter(email=request_user).exists()
        return False

    def get_user_saved(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.saved_by_users.filter(email=request_user).exists()
        return False
    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_mention_users(self, obj):
        return [mention_user.username for mention_user in obj.mention_users.all()]


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

    def get_user_username(self, obj):
        return obj.user.username 

    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            # If request object is not available, construct the URL manually based on the site domain
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    # def get_share_post(self, obj):
    #     # You can generate the share link based on your project's URL structure
    #     link = obj.get_absolute_url(obj.id)
    #     return link
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = TweetPostModel
        fields = ['aspect_ratio','tags','comments','premium','options','voice','link','file','media','cover','private','request_status',
                'user_followed','likes','id', 'photo_blur_hash','height', 'user',
                'user_username','user_liked','user_saved','user_viewed' ,'profile_image_url',
                'user_full_name','title', 'caption', 'hashtag', 'location','urls', 
                'category', 'created_date','updated_date','photo','video','total_views','total_shares',
                'share_post','total_saves','total_comments','total_likes','mention_users','likes']

class PodcastPostSerializer(serializers.ModelSerializer):
    user_username = serializers.SerializerMethodField()
    profile_image_url  = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    share_post = serializers.SerializerMethodField()  # Add this field

    mention_users = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    user_saved = serializers.SerializerMethodField()
    user_viewed = serializers.SerializerMethodField()
    def get_user_viewed(self, obj):
        # Get the current request user
        request_user = self.context['request'].user
        if request_user.is_authenticated:
            return obj.viewed_by_users.filter(email=request_user).exists()
        return False
    def get_user_saved(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.saved_by_users.filter(email=request_user).exists()
        return False

    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request'].user

        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_full_name(self, obj):
        return obj.user.full_name
    def get_mention_users(self, obj):
        return [mention_user.username for mention_user in obj.mention_users.all()]
    def get_user_username(self, obj):
        return obj.user.username 

    def get_profile_image_url(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            # If request object is not available, construct the URL manually based on the site domain
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    def get_share_post(self, obj):
        # You can generate the share link based on your project's URL structure
        request = self.context.get('request')
        share_url = f"{settings.SITE_DOMAIN}/posts/api/tweet/get/{obj.id}/"
        return share_url
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = PodcastPostModel
        fields = ['id', 'user','user_username','user_liked', 'user_viewed','user_saved','profile_image_url', 'user_full_name','title', 'caption', 'hashtag', 'location','urls', 'category', 'created_date',
                'updated_date','podcast',
                'total_views','total_shares','share_post','total_saves','total_comments','total_likes','mention_users']

class BookPostSerializer(serializers.ModelSerializer):
    class Meta:
        # total_likes = serializers.SerializerMethodField()
        shared_by_users = serializers.SerializerMethodField()
        total_views = serializers.SerializerMethodField()
        model = BookPostModel
        fields = ['id', 'user', 'title', 'caption', 'hashtag', 'location','urls','mention', 'category', 'created_date',
                'updated_date','book',
                'total_views','total_shares','total_saves','total_comments','total_likes']



class TweetPostCreateSerializer(serializers.ModelSerializer):
    # urls = serializers.ListField(child=serializers.CharField(max_length=255), required=False)
    # location = CustomCountryField(required=False)
    class Meta:
        model = TweetPostModel
        fields = ['aspect_ratio','link','file','cover','title', 'photo_blur_hash','height', 'caption', 'hashtag', 'location', 'category', 'urls','voice','photo','video','mention_users']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BookPostCreateSerializer(serializers.ModelSerializer):
    # urls = serializers.ListField(child=serializers.CharField(max_length=255), required=False)

    class Meta:
        model = BookPostModel
        fields = ['title', 'caption', 'hashtag', 'location', 'category','sub_category', 'urls','book']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class PodcastPostCreateSerializer(serializers.ModelSerializer):
    # urls = serializers.ListField(child=serializers.CharField(max_length=255), required=False)

    class Meta:
        model = PodcastPostModel
        fields = ['title', 'caption', 'hashtag', 'location', 'category','sub_category', 'urls','podcast']
    def create(self, validated_data):
        # Automatically set the 'user' field to the currently logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)






class CommentBaseSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField() 
    user_liked = serializers.SerializerMethodField()
    voice = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    class Meta:
        abstract = True
        fields = ['id','request_status','private','user_followed','text','voice','user_id','username','profile_image','total_likes','created_at','full_name','user_liked']
    def get_voice(self,obj):
        if obj.voice:
            return f"{settings.SITE_DOMAIN}{obj.voice.url}" 
        return None

    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request'].user
        # Check if the request user has liked this post
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_id(self, obj):
        return obj.user.id

    def get_full_name(self, obj):
        return obj.user.full_name

    def get_username(self, obj):
        return obj.user.username
    def get_profile_image(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    def create(self, validated_data):
        print(validated_data)
        # Automatically set the user based on the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
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

    def get_private(self,obj):
        return obj.user.private

    def get_user_followed(self, obj):
        request_user = self.context['request'].user
        if request_user.is_authenticated:
            # Assuming each user has one FollowModel instance associated with them
            follow_model = FollowModel.objects.filter(user=request_user).first()
            if follow_model:
                if follow_model.is_following(obj.user) == False:
                    return True
                else:
                    return False 
        return False
    # def validate(self, attrs):
    #     """
    #     Check that either the voice or text is provided.
    #     """
    #     voice = attrs.get('voice')
    #     text = attrs.get('text')

        # # Check if both voice and text are missing
        # if not voice or not text:
        #     raise serializers.ValidationError("Either voice or text must be provided.")

        # # Continue with the default validation after custom checks
        # return super().validate(attrs)

class CommentBaseWebSocketSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField() 
    user_liked = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        fields = ['id','text','user_id','username','profile_image','total_likes','created_at','full_name','user_liked']
    
    def get_user_liked(self, obj):
        # Get the current request user
        request_user = self.context['request']
        # Check if the request user has liked this post
        if request_user.user:
            request_user = request_user.user
        if request_user.is_authenticated:
            return obj.likes.filter(email=request_user).exists()
        return False

    def get_user_id(self, obj):
        return obj.user.id

    def get_full_name(self, obj):
        return obj.user.full_name

    def get_username(self, obj):
        return obj.user.username
    def get_profile_image(self, obj):
        if obj.user.profile_image:
            request = self.context.get('request')
            return f"{settings.SITE_DOMAIN}{obj.user.profile_image.url}"
        else:
            return None
    def create(self, validated_data):
        # Automatically set the user based on the request
        validated_data['user'] = self.context['request']
        return super().create(validated_data)



class TweetCommentWebSocketSerializer(CommentBaseWebSocketSerializer):
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=TweetPostModel.objects.all(),
        source='post'
    )

    class Meta(CommentBaseWebSocketSerializer.Meta):
        model = TweetCommentModel
        fields = CommentBaseWebSocketSerializer.Meta.fields + ['post_id']



class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        # Ensure the serializer calls itself for the representation of replies
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class TweetCommentSerializer(CommentBaseSerializer):
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    voice = serializers.FileField(max_length=None, allow_empty_file=False, use_url=True, required=False)

    class Meta(CommentBaseSerializer.Meta):
        model = TweetCommentModel
        fields = CommentBaseSerializer.Meta.fields + ['replies', 'replies_count', 'pinned', 'pinned_at']

    def get_replies(self, obj):
        # Filter replies to exclude hidden ones for the current user
        user = self.context['request'].user
        replies = obj.replies.all()
        filtered_replies = [reply for reply in replies if not reply.hidden_by_users.filter(id=user.id).exists()]

        # Serialize filtered replies
        return TweetCommentSerializer(filtered_replies, many=True, context=self.context).data

    def get_replies_count(self, obj):
        # Adjust this method to count only non-hidden replies if needed
        return self.get_replies(obj).__len__()

    def to_representation(self, instance):
        representation = super(TweetCommentSerializer, self).to_representation(instance)
        # Further customize the representation if needed, e.g., to filter nested replies
        return representation
    
    # def validate(self, data):
        # """
        # Check that either text or voice is provided.
        # # """
        # if not data.get('text') or not data.get('voice'):
        #     raise serializers.ValidationError("Either text or a voice note must be provided.")
        # if data.get('text') and data.get('voice'):
        #     raise serializers.ValidationError("Cannot provide both text and a voice note.")
        # return data
class TweetReplyCommentSerializer(CommentBaseSerializer):
    class Meta(CommentBaseSerializer.Meta):
        model = TweetReplyCommentModel








