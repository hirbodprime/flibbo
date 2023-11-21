# serializers.py
from rest_framework import serializers
from notification.models import UserDeviceModel
from notification.extract_ip import get_user_ip
class UserDeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceModel
        fields = ('id','user', 'user_token', 'device_type')
        read_only_fields = ('user',)
    def create(self, validated_data):
        request = self.context.get("request")
        user_ip = get_user_ip(request)
        if request and hasattr(request, "user"):
            validated_data['user'] = request.user
            if user_ip:
                validated_data['user_ip'] = user_ip
        return super(UserDeviceModelSerializer, self).create(validated_data)