from rest_framework import serializers
from activity.models import Activity
from django.core.exceptions import ObjectDoesNotExist
from following_system.models import FollowModel, RequestToFollow
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
            return request.build_absolute_uri(obj.user.profile_image.url)
        else:
            return None
    class Meta:
        model = Activity
        fields = ['user_followed','request_status','private','user_id','user_username','user_full_name','profile_image_url','activity_type','created_at','tweet','followed_user']
