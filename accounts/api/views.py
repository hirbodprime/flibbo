import requests
from rest_framework import generics as gn
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from marketplace.models import NftProductModel
from accounts.permissions import IsOwnerOrReadOnly
from accounts.models import CustomUser , SavedByUser, ReportUser,AccessToken,BlockModel,ChangeUsernameModel
from posts.models import TweetPostModel , PodcastPostModel, BookPostModel
from posts.api.serializers import TweetPostSerializer
from point.models import ReferralCodeModel
from point.point_functionality import process_referral_signup
from wallet.models import UsersNfts
from .serializers import ( UserLoginSerializer , LogoutSerializer,
 CustomUserSerializer, SignupSerializer,ShowCustomUserSerializer,
 ProfileSerializer,UserSignupValidationSerializer,UsernameValidationSerializer,
 UsernameCheckSerializer,PasswordResetSerializer,CustomUsersListSerializer,ReportUserSerializer,UserSerializer,AccessTokenLoginSerializer,CheckLoginSerializer,BlockModelSerializer,ReportReasonsSerializer,CustomAppleSocialLoginSerializer,CustomGoogleSocialLoginSerializer
 ,ChangeUsernameSerializer,ChangePasswordSerializer,AddBonusCodeSerializer,ChangePasswordFLSerializer,EmailCheckSerializer
 ,UsernameCheckSerializer)
from explore.custom_pagination import CustomPagination,CustomPagination2

from following_system.models import FollowModel,RequestToFollow
from tokens.models import TokenModel  # Import your Token model
import base64
from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404

from django.db.models import Q, Case, When, Value, IntegerField
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  permission_classes
from rest_framework.decorators import api_view
from accounts.models import report_reasons_choices

from django.contrib.auth import login
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


from django.utils import timezone
from datetime import timedelta
from django.db.models import Max

User = get_user_model()

@api_view(['POST'])
def check_username_exists(request):
    serializer = UsernameCheckSerializer(data=request.data)

    if serializer.is_valid():
        username = serializer.validated_data['username']

        # Check if the email exists in the database
        if CustomUser.objects.filter(username=username).exists():
            return Response({'detail': 'This username already exists.',"success":True}, status=status.HTTP_200_OK)

        return Response({'detail': 'This username does not exist.',"success":False}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_email_exists(request):
    serializer = EmailCheckSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        # Check if the email exists in the database
        if CustomUser.objects.filter(email=email).exists():
            return Response({'detail': 'This email already exists.',"success":True}, status=status.HTTP_200_OK)

        return Response({'detail': 'This email does not exist.',"success":False}, status=status.HTTP_404_NOT_FOUND)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddBonusApiview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the user already has a bonus code
        if user.bonus_code:
            return Response({
                'message': 'User already has a registered point.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddBonusCodeSerializer(data=request.data)
        if serializer.is_valid():
            bonus_code = serializer.validated_data.get('bonus_code')

            # Rest of your code for making the external API call
            # ...

            # Assuming the external API call is successful and response.status_code == 201
            # Save the bonus code to the user model
            user.bonus_code = bonus_code
            user.save()

            return Response({
                'data': {'bonus_code': bonus_code},
                'success': True
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"message": "Wrong Old password."}, 
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully"}, 
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError

# ... rest of your code ...

class ChangePasswordFLUsersView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordFLSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email=serializer.validated_data['email'])
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                # Log the exception here if needed
                return Response({"message": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangeUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangeUsernameSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Check if the user has changed username in the last 15 days
            last_change = ChangeUsernameModel.objects.filter(
                user=user
            ).aggregate(last_change=Max('started_at')).get('last_change')

            # Check if this change was within the last 15 days
            if last_change and (timezone.now() - last_change) < timedelta(days=15):
                return Response(
                    {"error": "You can only change your username every 15 days."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Save old username with a 15-day restriction
            ChangeUsernameModel.objects.create(
                user= user,
                username=user.username, 
                started_at=timezone.now(), 
                ended_at=timezone.now() + timedelta(days=15)
            )

            # Change username
            user.username = serializer.validated_data['new_username']
            user.save()

            return Response({"message": "Username changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(SocialLoginView): # if you want to use Implicit Grant, use this
    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomGoogleSocialLoginSerializer
    def post(self, request, *args, **kwargs):
        try:
            # Process the social login request
            response = super().post(request, *args, **kwargs)
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            # Add additional data to the response\
            user = request.user
            profile_image_url = f"{settings.SITE_DOMAIN}{user.profile_image.url}" if user.profile_image else None
            user_data = {
                'id': user.id,
                'username': user.username,
                'followers_count': user.followers_count,
                'followings_count': user.followings_count,
                'email': user.email,
                'full_name': user.full_name,
                'join_date':user.join_date,
                'birthday': user.birthday,
                'country': user.country,
                # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url}' if user.profile_image else None,  
                'profile_image': profile_image_url,  
                'bio':user.bio,
                'facebook_url':user.facebook_url,
                'twitter_url':user.twitter_url,
                'instagram_url':user.instagram_url,
                'linkedin_url':user.linkedin_url,
            }
            email = str(request.user)

            response.data["user_data"] = user_data
            response.data["access"] = access_token
            response.data["refresh"] = refresh_token

            return response
        except OAuth2Error as e:
            error_message = str(e) if str(e) else 'OAuth2 authentication failed'
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)




class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    client_class = AppleOAuth2Client
    
    serializer_class = CustomAppleSocialLoginSerializer
    def post(self, request, *args, **kwargs):
        try:
            # Process the social login request
            response = super().post(request, *args, **kwargs)
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            # Add additional data to the response\
            user = request.user
            profile_image_url = f"{settings.SITE_DOMAIN}{user.profile_image.url}" if user.profile_image else None
            user_data = {
                'id': user.id,
                'username': user.username,
                'followers_count': user.followers_count,
                'followings_count': user.followings_count,
                'email': user.email,
                'full_name': user.full_name,
                'join_date':user.join_date,
                'birthday': user.birthday,
                'country': user.country,
                # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url}' if user.profile_image else None,  
                'profile_image': profile_image_url,  
                'bio':user.bio,
                'facebook_url':user.facebook_url,
                'twitter_url':user.twitter_url,
                'instagram_url':user.instagram_url,
                'linkedin_url':user.linkedin_url,
            }
            email = str(request.user)

            response.data["user_data"] = user_data
            response.data["access"] = access_token
            response.data["refresh"] = refresh_token

            return response
        except OAuth2Error as e:
            # Handle the OAuth2Error here
            error_message = str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

class BlockedUsersListView(APIView):

    def get(self, request, user_id):
        try:
            # Get the BlockModel object for the user with the given ID
            block_instance = BlockModel.objects.get(user__id=user_id)
        except BlockModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the list of blocked users
        blocked_users = block_instance.blocked_users.all()

        # Serialize the blocked users
        serializer = UserSerializer(blocked_users, context={'request':request},many=True)

        response_data  = {
            'data':serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class SavedTweetsMediaListView(gn.ListAPIView):
    serializer_class = TweetPostSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Get the user_id from the URL kwargs
        user_saved,created = SavedByUser.objects.get_or_create(user_id=user_id)
        
        # Fetch the saved tweets and exclude those without images and videos
        return user_saved.saved_tweets.exclude(Q(photo__exact="") & Q(video__exact=""))

class SavedTweetsTextListView(gn.ListAPIView):
    serializer_class = TweetPostSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Get the user_id from the URL kwargs
        user_saved,created = SavedByUser.objects.get_or_create(user_id=user_id)
        
        # Fetch the saved tweets and exclude those without images and videos
        return user_saved.saved_tweets.filter(photo__exact="", video__exact="")


class BlockUserView(gn.CreateAPIView):
    queryset = BlockModel.objects.all()
    serializer_class = BlockModelSerializer

    def create(self, request, user_id=None, *args, **kwargs):
        blocked_user = get_object_or_404(User, id=user_id)
        block_instance, created = BlockModel.objects.get_or_create(user=request.user)
        user_getting_blocked_obj, created = BlockModel.objects.get_or_create(user=blocked_user)
        block_instance.blocked_users.add(blocked_user)
        user_getting_blocked_obj.blocked_by.add(request.user)
        serializer = BlockModelSerializer(block_instance)

        user_creating_unfollow_followmodel,created = FollowModel.objects.get_or_create(user=block_instance.user)
        user_getting_unfollow_followmodel,created = FollowModel.objects.get_or_create(user=blocked_user)
        user_getting_unfollow_followmodel.following.remove(block_instance.user)
        user_creating_unfollow_followmodel.followers.remove(blocked_user)
        user_creating_unfollow_followmodel.unfollow(blocked_user)
        user_getting_unfollow_followmodel.user.followers_count -= 1
        user_creating_unfollow_followmodel.user.followings_count -= 1
        user_creating_unfollow_followmodel.user.save()
        user_getting_unfollow_followmodel.user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UnblockUserView(gn.DestroyAPIView):
    queryset = BlockModel.objects.all()
    serializer_class = BlockModelSerializer

    def destroy(self, request, user_id=None, *args, **kwargs):
        blocked_user = get_object_or_404(User, id=user_id)
        block_instance = get_object_or_404(BlockModel, user=request.user)
        blocked_user_instance = get_object_or_404(BlockModel, user=blocked_user)
        blocked_user_instance.blocked_by.remove(block_instance.user)
        block_instance.blocked_users.remove(blocked_user)
        return Response(status=status.HTTP_204_NO_CONTENT)



class AccessTokenLoginView(APIView):
    def post(self, request):
        serializer = AccessTokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']

        try:
            access_token = AccessToken.objects.get(token=token)
        except AccessToken.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # At this point, the token is valid and the user associated with the token is authenticated
        request.user = access_token.user  # Associate user with request

        # For traditional session-based login (uncommon in REST APIs)
        login(request, access_token.user,backend='accounts.custom_authentication.UsernameBackend')
        
        return Response({"message": "Successfully authenticated"}, status=status.HTTP_200_OK)


from explore.custom_pagination import CustomPagination


@permission_classes([IsAuthenticated])
class UserSearchView(APIView):
    def get(self, request, query=None):
        if query:
            block_obj,created = BlockModel.objects.get_or_create(user=request.user)
            users_blocked_by_current_user = block_obj.blocked_users.all()

            # Step 2: Get users who have blocked the current user
            users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=request.user)
            blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
            # Step 3: Combine the lists
            blocked_usernames_combined = list(users_blocked_by_current_user.values_list('username', flat=True)) + list(blocked_by_users_obj.values_list('username', flat=True))
            print(blocked_usernames_combined)
            users = CustomUser.objects.exclude(username__in=blocked_usernames_combined).filter(
                Q(username__istartswith=query) | 
                Q(username__icontains=query)
            ).annotate(
                priority=Case(
                    When(username__istartswith=query, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('priority', 'username')
            
            paginator = CustomPagination()
            paginator.page_size = 10  # Set the number of items per page
            result_page = paginator.paginate_queryset(users, request)
            serializer = CustomUserSerializer(result_page, many=True)
            response_data = {
                "data":serializer.data
                
            }
            return paginator.get_paginated_responsee(serializer.data)
        else:
            return []
            
class CheckLoginStatusAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CheckLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                
                # Create a new token manually
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
            
                profile_image_url = f"{settings.SITE_DOMAIN}/{user.profile_image.url}" if user.profile_image else None
                user_token = AccessToken.objects.get(user=user)
                user_data = {
                    
                    'id': user.id,
                    'username': user.username,
                    'followers_count': user.followers_count,
                    'followings_count': user.followings_count,
                    'email': user.email,
                    'full_name': user.full_name,
                    'join_date':user.join_date,
                    'birthday': user.birthday,
                    'country': user.country,
                    # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url}' if user.profile_image else None,  
                    'profile_image': profile_image_url,  
                    'bio':user.bio,
                    'facebook_url':user.facebook_url,
                    'twitter_url':user.twitter_url,
                    'instagram_url':user.instagram_url,
                    'linkedin_url':user.linkedin_url,
                }
                return Response({
                    'token': str(user_token.token),
                    'found': True,
                    'user_data':user_data,
                    'refresh': refresh_token,
                    'access': access_token
                }, status=status.HTTP_200_OK)
                
            except CustomUser.DoesNotExist:
                return Response({'found': False}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    try:
        # Get the user
        user = request.user
        # Perform any pre-delete actions, like archiving data if needed
        # ...

        # Finally, delete the user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# new 10
class DeleteAccountAPIView(gn.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        response = Response({'message': 'Account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        request.user.delete()
        return response



class ReportReasonsListAPIView(gn.ListAPIView):

    serializer_class = ReportReasonsSerializer

    def get_queryset(self):
        return [{"code": code, "reason": reason} for code, reason in report_reasons_choices]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'data':serializer.data
        }
        return Response(response_data)

class ReportUserCreateApiView(gn.CreateAPIView):
    # queryset = ReportUser.objects.all()
    serializer_class = ReportUserSerializer
    def get_queryset(self):
        queryset = ReportUser.objects.filter(user=user)
        return queryset
    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        report_obj, created = ReportUser.objects.get_or_create(user=user)

        report_obj.report_count += 1
        report_obj.reported_by.add(self.request.user)
        report_reasons = self.request.data.get('report_reasons', None)
        if report_reasons:
            report_obj.report_reasons = report_reasons

        report_obj.save()

class CustomUsersListApiView(gn.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUsersListSerializer
    pagination_class = CustomPagination2

class PasswordResetApi(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_model = get_user_model()
            try:
                user = user_model.objects.get(email=email)
            except user_model.DoesNotExist:
                return Response({'detail': 'No user found with this email address.'}, status=status.HTTP_404_NOT_FOUND)

            # Generate a password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construct the password reset link
            # reset_link = reverse('reset_password_api')
            reset_link = f"{settings.SITE_DOMAIN}/?uid={uid}&token={token}"

            # Send the reset link in the response
            # Create the email subject and message
            subject = 'Password Reset Link'
            message = f'Click the following link to reset your password:\n\n{reset_link}'

            # Send the email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return Response({'detail': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)











from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator

class PasswordResetConfirmApi(APIView):
    def post(self, request, *args, **kwargs):
        uid = request.query_params.get('uid')
        token = request.query_params.get('token')
        new_password = request.data.get('new_password')
        confirm_new_password = request.data.get('confirm_new_password')
        print(uid)
        if new_password and confirm_new_password:
            try:
                uid = force_str(urlsafe_base64_decode(uid))
                user = get_user_model().objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                if new_password == confirm_new_password:
                    user.set_password(new_password)
                    user.save()
                    return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid reset link or passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)









from following_system.models import RequestToFollow 
from following_system.api.serializers import RequestToFollowListSerializer



class UserProfileApiView(gn.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ShowCustomUserSerializer
    # permission_classes = [IsAuthenticated]
    # def get_object(self):
    #     return self.request.user

    def retrieve(self, request, *args, **kwargs):
        if request.user:
            user_id = kwargs.get('id')  # 'pk' is the default URL parameter name for the object's primary key
            user = get_object_or_404(CustomUser, id=user_id)
            user_token = AccessToken.objects.get(user=user)

            current_site = get_current_site(request)
            domain = current_site.domain
            user_tweets = TweetPostModel.objects.filter(user=user)
            serializer = ShowCustomUserSerializer(user, context={'request': request,'user_id':user})
            request_activities = RequestToFollow.objects.filter(request_sender=request.user, requset_reciever=user).first()
            serializer_requests = RequestToFollowListSerializer(instance=request_activities, context={'request': request})
            tweet_serializer = TweetPostSerializer(
                user_tweets,
                many=True,
                context={'request': request}  # Include the request object in context
            )
            response_data = {
                'token': str(user_token.token),
                'request': serializer_requests.data,
                'user_data': serializer.data,
                'user_tweets': tweet_serializer.data,
                'success': True,
            }
            tweet_serializer = TweetPostSerializer(
                user_tweets,
                many=True,
                context={'request': request}  # Include the request object in context
            )

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileV2ApiView(gn.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ShowCustomUserSerializer
    permission_classes = [IsAuthenticated]
    # def get_object(self):
    #     return self.request.user

    def retrieve(self, request, *args, **kwargs):
        if request.user:
            username = kwargs.get('username')  # 'pk' is the default URL parameter name for the object's primary key
            user = get_object_or_404(CustomUser, username=username)
            user_token = AccessToken.objects.get(user=user)

            current_site = get_current_site(request)
            domain = current_site.domain
            user_tweets = TweetPostModel.objects.filter(user=user)
            serializer = ShowCustomUserSerializer(user, context={'request': request,'user_id':user.id})
            request_activities = RequestToFollow.objects.filter(request_sender=request.user, requset_reciever=user).first()
            serializer_requests = RequestToFollowListSerializer(instance=request_activities, context={'request': request})
            tweet_serializer = TweetPostSerializer(
                user_tweets,
                many=True,
                context={'request': request}  # Include the request object in context
            )
            response_data = {
                'token': str(user_token.token),
                'request': serializer_requests.data,
                'user_data': serializer.data,
                'user_tweets': tweet_serializer.data,
                'success': True,
            }
            tweet_serializer = TweetPostSerializer(
                user_tweets,
                many=True,
                context={'request': request}  # Include the request object in context
            )

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)






class UsernameCheckView(gn.CreateAPIView):
    serializer_class = UsernameCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return Response({'success': True}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class GenericDataValidationView(gn.CreateAPIView):
    serializer_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            # print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsernameValidationView(GenericDataValidationView):
    serializer_class = UsernameValidationSerializer

class DataValidationView(gn.CreateAPIView):
    serializer_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return Response({'success': True}, status=status.HTTP_200_OK)
        else:
            # print(request.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSignupValidationView(DataValidationView):
    serializer_class = UserSignupValidationSerializer


class UserLoginView(gn.CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        # print('here')
        serializer = self.get_serializer(data=request.data)
        # print(serializer)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        if '@' in username:
            user = authenticate(request=self.request, email=username, password=password,backend='accounts.custom_authentication.UsernameBackend')
            print(username,password)
        else:
            user = authenticate(request=self.request, username=username, password=password,backend='accounts.custom_authentication.UsernameBackend')

        if user is not None:
            # User authentication is successful
            login(request, user) 
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Create or update the tokens in the Token model
            token, created = TokenModel.objects.get_or_create(user=user)
            token.access_token = access_token
            token.refresh_token = refresh_token
            token.save()
            current_site = get_current_site(request)
            domain = current_site.domain
            user_token = AccessToken.objects.get(user=user)

            profile_image_url = f"{settings.SITE_DOMAIN}{user.profile_image.url}" if user.profile_image else None
            user_data = {
                
                'id': user.id,
                'username': user.username,
                'private': user.private,
                'followers_count': user.followers_count,
                'followings_count': user.followings_count,
                'email': user.email,
                'full_name': user.full_name,
                'join_date':user.join_date,
                'birthday': user.birthday,
                'country': user.country,
                # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url}' if user.profile_image else None,  
                'profile_image': profile_image_url,  
                'bio':user.bio,
                'facebook_url':user.facebook_url,
                'twitter_url':user.twitter_url,
                'instagram_url':user.instagram_url,
                'linkedin_url':user.linkedin_url,
            }
            return Response({'token': str(user_token.token),'user_data':user_data,'access_token': access_token, 'refresh_token': refresh_token,'success': True}, status=status.HTTP_200_OK)
        else:
            # User authentication failed
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
# from point.signals import referral_signup_signal

class SignupConfirmationView(gn.CreateAPIView):
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.backend = 'accounts.custom_authentication.UsernameBackend'
            user.set_password(request.data['password'])
            user.save()
            login(request, user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Create or update the tokens in the Token model
            token, created = TokenModel.objects.get_or_create(user=user)
            token.key = access_token  # Update the token key
            token.save()
            current_site = get_current_site(request)
            domain = current_site.domain

            profile_image_url = f"{settings.SITE_DOMAIN}{user.profile_image.url}" if user.profile_image else None
            user_token = AccessToken.objects.get(user=user)

            user_data = {
                'id':user.id,
                'username': user.username,
                'email': user.email,
                'private': user.private,
                'full_name': user.full_name,
                'birthday': user.birthday,
                # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url}' if user.profile_image else None,  
                'profile_image': profile_image_url,
                'join_date': user.join_date,
                'followers_count': user.followers_count,
                'followings_count': user.followings_count,
                'bio':user.bio,
                'facebook_url':user.facebook_url,
                'twitter_url':user.twitter_url,
                'instagram_url':user.instagram_url,
                'linkedin_url':user.linkedin_url,
                'country':user.country,
            }
            # Instead of directly accessing the key, use the .get() method
            from point.models import PointWalletModel
            PointWalletModel.objects.create(user=user)
            referral_code = request.data.get('referral_code', None)
            if referral_code:
                try:
                    referrer = ReferralCodeModel.objects.get(ref_code=referral_code).user
                    ReferralCodeModel.objects.create(referrer=referrer, user=user)
                    process_referral_signup(new_user=user, referral_code=referral_code)
                except ReferralCodeModel.DoesNotExist:
                    print("Invalid referral code:", referral_code)
            else:
                ReferralCodeModel.objects.create(user=user)
                
            print(referral_code)
            return Response({
                        'token': str(user_token.token),
                        'user_data':user_data,
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'success': True
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .serializers import ProfileSerializer,SavedByUserSerializer
from django.core import serializers
import json

class ProfileApiView(gn.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        if request.user:
            print('geg')
            user = request.user
            current_site = get_current_site(request)
            domain = current_site.domain

            profile_image_url = f"{settings.SITE_DOMAIN}{user.profile_image.url}" if user.profile_image else None
            # print(profile_image_url)
            
            user_token = AccessToken.objects.get(user=user)
            print(user_token)
            user_data = {
                
                'id': user.id,
                'username': user.username,
                'private': user.private,
                'email': user.email,
                'full_name': user.full_name,
                'followers_count': user.followers_count,
                'followings_count': user.followings_count,
                'birthday': user.birthday,
                # 'profile_image': f'http://192.168.3.73:8000{user.profile_image.url if user.profile_image else None}',  
                'profile_image': profile_image_url,
                'bio':user.bio,
                'join_date':user.join_date,
                'facebook_url':user.facebook_url,
                'twitter_url':user.twitter_url,
                'instagram_url':user.instagram_url,
                'linkedin_url':user.linkedin_url,
                'country':user.country,
            }
            user = self.request.user
            serializer = CustomUserSerializer(user, context={'request': request})

            response_data = {
                'token': str(user_token.token),
                'user_data': serializer.data,
                'success': True,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)















from .serializers import SavedByUserSerializer

class SavedPostsApiView(gn.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SavedByUserSerializer
    # permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user
    def retrieve(self, request, *args, **kwargs):
        if request.user:
            user = request.user
            current_site = get_current_site(request)
            domain = current_site.domain

            
            profile_image_url = f"{settings.SITE_DOMAIN}/{user.profile_image.url}" if user.profile_image else None
            saved_posts = SavedByUser.objects.filter(user=user)
            saved_tweets_list = []
            
            for saved_post in saved_posts:
                saved_tweets = saved_post.saved_tweets.all()  # Use .all() to access the related saved tweets
                for saved_tweet in saved_tweets:
                    if saved_tweet.photo:
                        photo = f"{settings.SITE_DOMAIN}/{saved_tweet.photo.url}"
                        
                    else:
                        photo = None
                    if saved_tweet.video:
                        video = f"{settings.SITE_DOMAIN}/{saved_tweet.video.url}"
                    else:
                        video = None
                    share_url = f"{settings.SITE_DOMAIN}/posts/api/tweet/get/{saved_tweet.id}"
                    
                    mention_users = [mention_user.username for mention_user in saved_tweet.mention_users.all()]
                    
                    used_liked = saved_tweet.likes.filter(email=request.user).exists()
                    user_liked = True if used_liked else False
                    
                    used_viewed = saved_tweet.viewed_by_users.filter(email=request.user).exists()
                    user_viewed = True if used_viewed else False

                    used_saved = saved_tweet.saved_by_users.filter(email=request.user).exists()
                    user_saved = True if used_saved else False

                    user_id = saved_tweet.user
                    restatus = None
                    try:
                        request_follow_obj = RequestToFollow.objects.get(
                            requset_reciever=saved_tweet.user,  # The user who will receive the request
                            request_sender=user   # The user who sent the request
                        )
                    except RequestToFollow.DoesNotExist:
                        request_follow_obj = None

                    if not request_follow_obj is None:
                        restatus = request_follow_obj.status
                    saved_tweet_dic = {
                        'private':saved_tweet.user.private,
                        'request_status':restatus,
                        'user':user_id.id,
                        'total_views':saved_tweet.total_views,
                        'profile_image':profile_image_url,
                        'total_shares':saved_tweet.total_shares,
                        'total_saves':saved_tweet.total_saves,
                        'total_comments':saved_tweet.total_comments,
                        'total_likes':saved_tweet.total_likes,
                        'id': saved_tweet.id,
                        'category': saved_tweet.category.name,
                        'user_liked': user_liked,
                        'user_viewed': user_viewed,
                        'user_saved': user_saved,
                        'mention_users':mention_users,
                        'share_post':share_url,
                        'video': video,
                        'photo': photo,
                        'title': saved_tweet.title,
                        'user_full_name': saved_tweet.user.full_name,
                        'user_username': saved_tweet.user.username,
                        'slug': saved_tweet.slug,
                        'caption': saved_tweet.caption,
                        'location': "",
                        'hashtag': saved_tweet.hashtag,
                        'urls': saved_tweet.urls,
                        'created_date': saved_tweet.created_date,
                        'updated_date': saved_tweet.updated_date,
                    }
                    saved_tweets_list.append(saved_tweet_dic)
            serializer = SavedByUserSerializer(user, context={'request': request})
            response_data = {
                'saved_posts':saved_tweets_list,
                'success': True,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)



















class UpdateProfileApiView(gn.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer 
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        # Return the user making the request
        return self.request.user
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Check if 'profile_image' is in the request data
        if 'profile_image' in request.data:
            # Update the profile image
            if request.data['profile_image'] == 'del':
                instance.profile_image = None
                print('profile deleted')
            else:
                instance.profile_image = request.data['profile_image']

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = {
            'data':serializer.data
        }
        return Response(response_data)

class LogoutAPIView(gn.CreateAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user:
            # Get the user's token
            user =request.user
            token = TokenModel.objects.filter(user=user).first()

            # If the token exists, delete it
            if token:
                token.delete()
                return Response({"success": True, "detail": "User logged out successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Token not found. User might not be authenticated."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)





# authentication/views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
# class CustomTokenRefreshView(TokenRefreshView):
#     pass

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model  # Import the User model

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Get the current refresh token
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to decode the refresh token and get the user's ID
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get('user_id')
        except Exception as e:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the User model instance
        User = get_user_model()
        user = User.objects.get(id=user_id)

        # Create a new refresh token and a new access token
        new_refresh_token = RefreshToken.for_user(user)
        new_access_token = new_refresh_token.access_token

        # Return both the new access token and refresh token as a response
        response_data = {
            'access': str(new_access_token),
            'refresh': str(new_refresh_token),
        }

        return Response(response_data)
