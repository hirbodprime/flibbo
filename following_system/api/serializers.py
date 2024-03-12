from rest_framework import serializers
from following_system.models import FollowModel,RequestToFollow
from django.contrib.auth import get_user_model
from activity.models import Activity
from django.conf import settings
User = get_user_model()


class RequestToFollowStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestToFollow
        fields = ['status']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

# 'profile_image': profile_image_url,
# 'username': user_obj.username,
# 'user_id': user_obj.id,
# 'full_name': user_obj.full_name,
# 'bio': user_obj.bio,
# 'user_followed': is_followed

class RequestToFollowListSerializer(serializers.ModelSerializer):
    sender_username = serializers.SerializerMethodField()
    sender_profile_image = serializers.SerializerMethodField()
    sender_full_name = serializers.SerializerMethodField()
    sender_bio = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()

    def get_is_following(self,obj):

        user_follow_model_obj, created = FollowModel.objects.get_or_create(user=obj.request_sender)
        # followers_users = user_follow_model_obj.followers.all()
        is_following = user_follow_model_obj.followers.filter(id=self.context['request'].user.id).exists()

        return is_following

    def get_private(self,obj):
        usere = CustomUser.objects.get(email=obj.request_sender)
        return usere.private
    def get_sender_username(self, obj):
        request_sender = obj.request_sender  # Assuming 'request_sender' is the foreign key to the User model
        return request_sender.username
    def get_sender_profile_image(self, obj):
        request_sender = obj.request_sender  # Assuming 'request_sender' is the foreign key to the User model
        if request_sender.profile_image:
            return f"{settings.SITE_DOMAIN}{request_sender.profile_image.url}"
        else:
            return None
        # return f'{request_sender.profile_image.url}'
    def get_sender_full_name(self, obj):
        request_sender = obj.request_sender  # Assuming 'request_sender' is the foreign key to the User model
        return request_sender.full_name
    def get_sender_bio(self, obj):
        request_sender = obj.request_sender  # Assuming 'request_sender' is the foreign key to the User model
        return request_sender.bio
    class Meta:
        model = RequestToFollow
        fields = ('id','requset_reciever','private','is_following','sender_username','sender_profile_image','sender_bio','sender_full_name','request_sender','status','created_at','updated_at')


class RequestToFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestToFollow
        fields = ('requset_reciever',)

    def create(self, validated_data):
        # Automatically fill the 'request_sender' field with the user sending the request
        user = self.context['request'].user
        receiver = validated_data.get('requset_reciever')

        # Check if there's an existing request with the same sender and receiver
        existing_request = RequestToFollow.objects.filter(
            request_sender=user,
            requset_reciever=receiver
        ).first()

        if existing_request:
            # Delete any related Activity objects for the existing request
            Activity.objects.filter(
                followed_user=existing_request.requset_reciever,
                user=existing_request.request_sender,
                activity_type=Activity.FOLLOW
            ).delete()
            
            # Delete the existing request
            existing_request.delete()

        # Create the new follow request
        request_to_follow = RequestToFollow.objects.create(request_sender=user, **validated_data)
        return request_to_follow


# class RequestToFollowSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RequestToFollow
#         fields = ('requset_reciever',)
#     def create(self, validated_data):
#         # Automatically fill the 'user' field with the user sending the request
#         user = self.context['request'].user
#         request_to_follow = RequestToFollow.objects.create(request_sender=user, **validated_data)
#         return request_to_follow

class FollowModelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowModel
        fields = '__all__'
        
from accounts.models import CustomUser


class FollowersModelListSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    class Meta:
        model = FollowModel
        fields = ['user', 'followers']

    def get_followers(self, obj):
        request = self.context.get('request')
        followers_users = obj.followers.all()
        data = []
        for user_obj in followers_users:
            usere = CustomUser.objects.get(email=user_obj)

            profile_image_url = f"{settings.SITE_DOMAIN}{user_obj.profile_image.url}" if user_obj.profile_image else None
            is_followed = obj.is_user_following(user_obj)
            status = None
            try:
                request_follow_obj = RequestToFollow.objects.get(
                    requset_reciever=user_obj,  # The user who will receive the request
                    request_sender=request.user   # The user who sent the request
                )
            except RequestToFollow.DoesNotExist:
                request_follow_obj = None

            if not request_follow_obj is None:
                status = request_follow_obj.status
            user_data = {
                'request_status': status,
                'premium': user_obj.premium,
                'private': usere.private,
                'profile_image': profile_image_url,
                'username': user_obj.username,
                'id': user_obj.id,
                'full_name': user_obj.full_name,
                'bio': user_obj.bio,
                'user_followed': is_followed
            }
            data.append(user_data)
        return data

class FollowingModelListSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    class Meta:
        model = FollowModel
        fields = ['user', 'following']

    def get_following(self, obj):
        request = self.context.get('request')
        following_users = obj.following.all()
        data = []
        for user_obj in following_users:
            usere = CustomUser.objects.get(email=user_obj)
            profile_image_url = f"{settings.SITE_DOMAIN}{user_obj.profile_image.url}" if user_obj.profile_image else None
            is_followed = obj.is_user_following(user_obj)
            status = None
            try:
                request_follow_obj = RequestToFollow.objects.get(
                    requset_reciever=user_obj,  # The user who will receive the request
                    request_sender=request.user   # The user who sent the request
                )
            except RequestToFollow.DoesNotExist:
                request_follow_obj = None

            if not request_follow_obj is None:
                status = request_follow_obj.status

            user_data = {
                'id': user_obj.id,
                'request_status': status,
                'private': usere.private,
                'profile_image': profile_image_url,
                'username': user_obj.username,
                'premium': user_obj.premium,
                'full_name': user_obj.full_name,
                'bio': user_obj.bio,
                'user_followed': is_followed
            }
            data.append(user_data)
        return data


class FollowModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowModel
        fields = ()
    def create(self, validated_data):
        # Get the user_id from the validated data
        user_id = self.context.get('user_id')

        # Get the user to follow
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'success': False, 'follow': 'User not found'})

        # Get the instance of the user creating the follow
        user_creating_follow = self.context['request'].user
        user_creating_follow_user_obj = User.objects.get(email=user_creating_follow)
        user_creating_follow_followmodel,created = FollowModel.objects.get_or_create(user=user_creating_follow)
        # Check if the user is already following
        if user_creating_follow_followmodel.is_following(user_to_follow) != False:
            # Call the follow method
            Activity.objects.create(user=user_creating_follow, followed_user=user_to_follow, activity_type=Activity.FOLLOW)
            user_creating_follow_user_obj.increment_followings_count()
            user_creating_follow_followmodel.follow(user_to_follow)
            user_to_follow.increment_followers_count()
            return {'success': True, 'follow': 'Successfully followed this user'}
        else:
            raise serializers.ValidationError({'success': False, 'follow': 'Already following this user'})



class UnFollowModelDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowModel
        fields = ()
    def create(self, validated_data):
        # Get the user_id from the validated data
        user_id = self.context.get('user_id')

        # Get the user to follow
        try:
            user_to_unfollow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'success': False, 'follow': 'User not found'})

        # Get the instance of the user creating the follow
        user_creating_unfollow = self.context['request'].user
        user_creating_unfollow_user_obj,created = User.objects.get_or_create(email=user_creating_unfollow)

        user_creating_unfollow_followmodel = FollowModel.objects.get(user=user_creating_unfollow)
        # Check if the user is already following
        if user_creating_unfollow_followmodel.is_following(user_to_unfollow) == False:
            # Call the follow method
            Activity.objects.create(user=user_creating_unfollow, followed_user=user_to_unfollow, activity_type=Activity.UNFOLLOW)
            user_creating_unfollow_user_obj.decrement_followings_count()
            user_creating_unfollow_followmodel.unfollow(user_to_unfollow)
            user_to_unfollow.decrement_followers_count()
            return {'success': True, 'follow': 'Successfully Unfollowed this user'}
        else:
            raise serializers.ValidationError({'success': False, 'follow': 'Not Following this User'})

class FollowModelRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowModel
        fields = '__all__'