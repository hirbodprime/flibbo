from rest_framework import serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from following_system.models import FollowModel
from accounts.models import SavedByUser,ChangeUsernameModel,CustomUser, ReportUser, BlockModel
from following_system.models import FollowModel,RequestToFollow
from accounts.custom_authentication import UsernameBackend

from dj_rest_auth.registration.serializers import SocialLoginSerializer
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from requests.exceptions import HTTPError
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model,authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth import load_backend, login as django_login
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
import requests
User = get_user_model()

class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.EmailField()


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField()

class AddBonusCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('bonus_code',)
    def validate(self, data):
        bonus_code = data.get("bonus_code")
        if bonus_code:
            print(bonus_code)
            url = f"https://panel.flhub.org/users/api/check-bonus-code/{bonus_code}/"
            response = requests.get(url)

            if response.status_code == 200:
                pass
            else:
                raise serializers.ValidationError({"error_bonus":"The Point Code is wronge!"})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # password_validation.validate_password(value)
        return value

class ChangePasswordFLSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value

class ChangeUsernameSerializer(serializers.ModelSerializer):
    new_username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['new_username']

    def validate_new_username(self, value):
         # Check if the new username is already in use
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError({"error":"This username is already in use."})

        # Check if the username was used in the past 15 days
        recent_use = ChangeUsernameModel.objects.filter(username=value, ended_at__gt=timezone.now() - timedelta(days=15)).exists()
        if recent_use:
            remaining_days = (ChangeUsernameModel.objects.get(username=value).ended_at - timezone.now()).days
            raise serializers.ValidationError({"error":f"This username cannot be used for another {remaining_days} days."})

        return value

class CustomGoogleSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _('View is not defined, pass it as a context variable'),
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_('Define adapter_class in view'))

        adapter = adapter_class(request)
        app = adapter.get_provider().app

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get('access_token')
        code = attrs.get('code')
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {'access_token': access_token}
            token = access_token
            # For sign in with apple
            id_token = attrs.get('id_token')
            if id_token:
                tokens_to_parse['id_token'] = id_token
            provider = adapter.get_provider()
        # Case 2: We received the authorization code
        elif code:
            self.set_callback_url(view=view, adapter_class=adapter_class)
            self.client_class = getattr(view, 'client_class', None)

            if not self.client_class:
                raise serializers.ValidationError(
                    _('Define client_class in view'),
                )

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            try:
                token = client.get_access_token(code)
            except OAuth2Error as ex:
                raise serializers.ValidationError(
                    _('Failed to exchange code for access token')
                ) from ex
            access_token = token['access_token']
            tokens_to_parse = {'access_token': access_token}

            # If available we add additional data to the dictionary
            for key in ['refresh_token', 'id_token', adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _('Incorrect input. access_token or code is required.'),
            )

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            if adapter.provider_id == 'google' and not code:
                login = self.get_social_login(adapter, app, social_token, response={'id_token': id_token})
            else:
                login = self.get_social_login(adapter, app, social_token, token)
            ret = complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_('Incorrect value'))

        if isinstance(ret, HttpResponseBadRequest):
            raise serializers.ValidationError(ret.content)

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            # if allauth_account_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
            account_exists = get_user_model().objects.filter(
                email=login.user.email,
            ).exists()
            
            if account_exists:
                # Retrieve the existing user
                existing_user = get_user_model().objects.get(email=login.user.email)
                
                # Perform login operation
                django_login(request, existing_user,backend='accounts.custom_authentication.UsernameBackend')
    
                # Set the user object in attrs
                attrs['user'] = existing_user
                return attrs


            login.lookup()
            login.save(request, connect=True)
            self.post_signup(login, attrs)

        user_obj = CustomUser.objects.get(email=login.account.user)
        if not user_obj.full_name:  
            user_obj.full_name = str(login.account)
            user_obj.save()
        attrs['user'] = login.account.user
        return attrs
        
class CustomAppleSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _('View is not defined, pass it as a context variable'),
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_('Define adapter_class in view'))

        adapter = adapter_class(request)
        app = adapter.get_provider().app

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        access_token = attrs.get('access_token')
        code = attrs.get('code')
        # Case 1: We received the access_token
        if access_token:
            tokens_to_parse = {'access_token': access_token}
            token = access_token
            # For sign in with apple
            id_token = attrs.get('id_token')
            if id_token:
                tokens_to_parse['id_token'] = id_token
            provider = adapter.get_provider()
        # Case 2: We received the authorization code
        elif code:
            self.set_callback_url(view=view, adapter_class=adapter_class)
            self.client_class = getattr(view, 'client_class', None)

            if not self.client_class:
                raise serializers.ValidationError(
                    _('Define client_class in view'),
                )

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope,
                scope_delimiter=adapter.scope_delimiter,
                headers=adapter.headers,
                basic_auth=adapter.basic_auth,
            )
            try:
                token = client.get_access_token(code)
            except OAuth2Error as ex:
                raise serializers.ValidationError(
                    _('Failed to exchange code for access token')
                ) from ex
            access_token = token['access_token']
            tokens_to_parse = {'access_token': access_token}

            # If available we add additional data to the dictionary
            for key in ['refresh_token', 'id_token', adapter.expires_in_key]:
                if key in token:
                    tokens_to_parse[key] = token[key]
        else:
            raise serializers.ValidationError(
                _('Incorrect input. access_token or code is required.'),
            )

        social_token = adapter.parse_token(tokens_to_parse)
        social_token.app = app

        try:
            if adapter.provider_id == 'google' and not code:
                login = self.get_social_login(adapter, app, social_token, response={'id_token': id_token})
            else:
                login = self.get_social_login(adapter, app, social_token, token)
            ret = complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_('Incorrect value'))

        if isinstance(ret, HttpResponseBadRequest):
            raise serializers.ValidationError(ret.content)

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if allauth_account_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = get_user_model().objects.filter(
                    email=login.user.email,
                ).exists()
                if account_exists:
                    raise serializers.ValidationError(
                        _('User is already registered with this e-mail address.'),
                    )

            login.lookup()
            login.save(request, connect=True)
            self.post_signup(login, attrs)

        user_obj = CustomUser.objects.get(email=login.account.user)
        if not user_obj.full_name:  
            user_obj.full_name = str(login.account)
            user_obj.save()
        attrs['user'] = login.account.user
        return attrs 
class UserSerializer(serializers.ModelSerializer):
    profile_image  = serializers.SerializerMethodField()
    private = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
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

    def get_private(self,obj):
        return obj.private
    def get_profile_image(self, obj):
        if obj.profile_image:
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.profile_image.url}"
        else:
            return None
    class Meta:
        model = User
        fields = ('user_followed','request_status','private','id', 'username', 'email','profile_image','full_name')  

        

class ReportReasonsSerializer(serializers.Serializer):
    reason = serializers.CharField()
    code = serializers.CharField()


class BlockModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockModel
        fields = ['id', 'user', 'blocked_users']
        read_only_fields = ['id', 'user', 'blocked_users']
class AccessTokenLoginSerializer(serializers.Serializer):
    token = serializers.CharField()


class CheckLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ReportUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportUser
        fields = ('id', 'user', 'reported_by','report_reasons')
        read_only_fields  = ('user', 'reported_by')

    def validate(self, data):
        """
        Custom validation to prevent duplicate reporting by the same user.
        """
        user = self.context['view'].kwargs.get('user_id')
        reported_by = self.context['request'].user

        already_reported = ReportUser.objects.filter(
            user_id=user,
            reported_by=reported_by
        ).exists()

        if already_reported:
            raise serializers.ValidationError({"message": "You have already reported this user"})

        return data



class CustomUsersListSerializer(serializers.ModelSerializer):
    profile_image  = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    def get_followers_count(self, obj):
        """
        Returns the count of followers for the user.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.followers.count()

    def get_followings_count(self, obj):
        """
        Returns the count of users the user is following.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.following.count()
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.profile_image.url}"
        else:
            return None
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'full_name', 'country', 'is_active', 'is_staff', 'join_date', 'birthday', 'last_username_change', 'bio', 'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'profile_image', 'private', 'followers_count', 'followings_count')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()



class ShowCustomUserSerializer(serializers.ModelSerializer):
    profile_image  = serializers.SerializerMethodField()
    user_followed = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    def get_followers_count(self, obj):
        """
        Returns the count of followers for the user.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.followers.count()

    def get_followings_count(self, obj):
        """
        Returns the count of users the user is following.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.following.count()
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.profile_image.url}"
        else:
            return None

    def get_user_followed(self, obj):
        other_user_id = self.context['user_id']
        request_user = self.context['request'].user
        follow_obj,created = FollowModel.objects.get_or_create(user=request_user)
        return follow_obj.is_user_following(other_user_id)

    class Meta:
        model = CustomUser
        fields = ('id', 'private', 'email', 'username', 'full_name', 'join_date', 'birthday','bio','user_followed', 'followers_count','followings_count',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url','profile_image','country')






from django_countries.fields import Country

class CountryFieldSerializer(serializers.Field):
    def to_representation(self, obj):
        if obj:
            return obj.code  # You can choose to use code or name
        return None

    def to_internal_value(self, data):
        if data:
            return Country(data)
        return None


class SavedByUserSerializer(serializers.ModelSerializer):
    # location = CountryFieldSerializer()
    class Meta:
        model = SavedByUser
        fields = ('user', 'saved_tweets')

class UserSignupValidationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(), message="Email is not unique")]
    )

    password = serializers.CharField(
        write_only=True, required=True, min_length=6
    )

    confirm_password = serializers.CharField(
        write_only=True, required=True, min_length=6
    )

    full_name = serializers.CharField(required=True)
    birthday = serializers.DateField(required=False,allow_null=True)
    # Add other fields here

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match!")

        # Validate the password using Django's built-in password validation
        # try:
        #     validate_password(password)
        # except serializers.ValidationError as e:
        #     raise serializers.ValidationError(e.messages[0])

        return data



class UsernameValidationSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(), message="This field is not unique")]
    )

    def validate(self, data):
        field_value = data.get("username")
        # Add any additional validation logic specific to the field here

        return data



class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get("username")

        # Check if the username exists in the database
        if '@' in username: 
            if User.objects.filter(email=username).exists():
                return data  # Username exists
            else:
                raise serializers.ValidationError({"username": "Username does not exist"})
        else:
            if User.objects.filter(username=username).exists():
                return data  # Username exists
            else:
                raise serializers.ValidationError({"username": "Username does not exist"})
            
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Replace with your User model
        fields = (
            'id',
            'username',
            'email',
            'full_name',
            'followers_count',
            'followings_count',
            'birthday',
            'private',
            'profile_image',
            'bio',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'linkedin_url',
            'join_date',
            'country',
        )
from accounts.models import SavedByUser
class SavedByUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedByUser
        fields = ('user', 'saved_tweets', 'saved_books', 'saved_podcasts', 'nfts_bought')
        
class CustomUserSerializer(serializers.ModelSerializer):
    profile_image  = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    followings_count = serializers.SerializerMethodField()
    def get_followers_count(self, obj):
        """
        Returns the count of followers for the user.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.followers.count()

    def get_followings_count(self, obj):
        """
        Returns the count of users the user is following.
        """
        follow_model_obj,created = FollowModel.objects.get_or_create(user=obj)
        return follow_model_obj.following.count()
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
            return f"https://{site_domain}{obj.profile_image.url}"
        else:
            return None
    class Meta:
        model = CustomUser
        fields = ('id', 'private', 'email', 'username', 'full_name', 'join_date', 'birthday','bio', 'followers_count','followings_count',
            'facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url','profile_image','country')
        read_only_fields = ('email','username','join_date','birthday','followers_count','followings_count',)   
    def update(self, instance, validated_data):
        # Update each field in validated_data only if it's provided, otherwise keep the existing data
        # instance.email = validated_data.get('email', instance.email)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.country = validated_data.get('country', instance.country)
        # instance.join_date = validated_data.get('join_date', instance.join_date)
        instance.birthday = validated_data.get('birthday', instance.birthday)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.facebook_url = validated_data.get('facebook_url', instance.facebook_url)
        instance.twitter_url = validated_data.get('twitter_url', instance.twitter_url)
        instance.instagram_url = validated_data.get('instagram_url', instance.instagram_url)
        instance.linkedin_url = validated_data.get('linkedin_url', instance.linkedin_url)
        instance.private = validated_data.get('private', instance.private)
        instance.save()
        return instance
        
        
class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()

    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # Add your user authentication logic here (e.g., using Django's built-in authentication)
        # You may use Django's authentication system or any custom logic you have.

        if not username or not password:
            raise serializers.ValidationError({'error':
                'Both username and password are required.'})

        user = authenticate(request=self.context.get(
            'request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError({'error':'Invalid credentials.'})

        data['user'] = user
        return data


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(), message="Email is not unique")]
    )

    confirm_password = serializers.CharField(
        write_only=True, required=True, min_length=6
    )
    birthday = serializers.DateField(required=False,allow_null=True)
    class Meta:
        model = User
        fields = ('username','email', 'full_name', 'birthday','password', 'confirm_password','bonus_code')
        extra_kwargs = {
            "password": {"write_only": True, "required": True, "min_length": 6}
        }

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.pop("confirm_password")
        bonus_code = data.get("bonus_code")
        if bonus_code:
            print(bonus_code)
            url = f"https://panel.flhub.org/users/api/check-bonus-code/{bonus_code}/"
            response = requests.get(url)

            if response.status_code == 200:
                pass
            else:
                raise serializers.ValidationError({"error_bonus":"The Bonus Code is wronge!"})
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match!")

        # Validate the password using Django's built-in password validation
        # try:
        #     validate_password(password)
        # except ValidationError:
        #     print("Password is too weak")
        #     raise serializers.ValidationError("Password is too weak")
        return data




from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Assuming 'email' is the field used for authentication
