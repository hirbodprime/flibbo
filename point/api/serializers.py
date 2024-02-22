from rest_framework import serializers
from point.models import WithDrawalRequestModel, RefMoneyModel, PointWalletModel, UserWalletModel, ReferralCodeModel
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    def get_profile_image(self,obj):
        if obj.profile_image:
            return f"{settings.SITE_DOMAIN}{obj.profile_image.url}"
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
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)  # Adjust max_digits and decimal_places as needed
    # def get_balance(self,obj):
    #     return float(obj.balance)
    class Meta:
        model = WithDrawalRequestModel
        fields = ['id', 'username', 'balance', 'created_at', 'status', 'status_failed']
        read_only_fields = ('user',)  # Make user read-only

    def create(self, validated_data):
        # Check if 'balance' is in validated_data
        if 'balance' not in validated_data:
            raise serializers.ValidationError({"balance": "Balance is required."})

        # If balance is present, proceed with creation
        return super().create(validated_data)
class WithDrawalRequestGetSerializer(serializers.ModelSerializer):
    # Optional: Include user as a read-only field to return it in the response
    username = serializers.ReadOnlyField(source='user.username')  # Or just 'user.id'
    balance = serializers.SerializerMethodField() # Adjust max_digits and decimal_places as needed
    def get_balance(self,obj):
        return float(obj.balance)
    class Meta:
        model = WithDrawalRequestModel
        fields = ['id', 'username', 'balance', 'created_at', 'status', 'status_failed']
        read_only_fields = ('user',)  # Make user read-only


class UserWalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWalletModel
        fields = ['id', 'wallet']  # Exclude 'user' from fields
    def validate_wallet(self, value):
        # Check if the wallet field is empty
        if not value:
            raise serializers.ValidationError("Wallet field cannot be empty.")
        return value

