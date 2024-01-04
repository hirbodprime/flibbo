from rest_framework import serializers
from point.models import WithDrawalRequestModel, RefMoneyModel, PointWalletModel, UserWalletModel, ReferralCodeModel
from django.contrib.auth import get_user_model
User = get_user_model()
dev_url = "dev.flxdevpanel.com"
app_url = "app.flxdevpanel.com"
class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    def get_profile_image(self,obj):
        if obj.profile_image:
            return f"https://{dev_url}{obj.profile_image.url}"
        return
    class Meta:
        model = User
        fields = ['id', 'username', 'join_date','profile_image']  # Add fields as needed

class RefMoneySerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    def get_balance(self,obj):
        return float(obj.balance)
    class Meta:
        model = RefMoneyModel
        fields = ['user','for_user', 'balance', 'created_at']


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCodeModel
        fields = ['ref_code', 'referrer']

class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWalletModel
        fields = ['wallet']

class PointWalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    def get_balance(self,obj):
        return float(obj.balance)
    class Meta:
        model = PointWalletModel
        fields = ['balance']

class WithDrawalRequestSerializer(serializers.ModelSerializer):
    # Optional: Include user as a read-only field to return it in the response
    username = serializers.ReadOnlyField(source='user.username')  # Or just 'user.id'
    balance = serializers.SerializerMethodField()
    def get_balance(self,obj):
        return float(obj.balance)
    class Meta:
        model = WithDrawalRequestModel
        fields = ['id', 'username', 'balance', 'created_at', 'status', 'status_failed']
        read_only_fields = ('user',)  # Make user read-only

    # Optionally, override create method if you need custom behavior
    def create(self, validated_data):
        # Custom creation logic here, if needed
        return super().create(validated_data)

class UserWalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWalletModel
        fields = ['id', 'wallet']  # Exclude 'user' from fields
    def validate_wallet(self, value):
        # Check if the wallet field is empty
        if not value:
            raise serializers.ValidationError("Wallet field cannot be empty.")
        return value

