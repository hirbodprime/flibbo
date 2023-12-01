from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (UserLoginView, SignupConfirmationView, LogoutAPIView,ProfileApiView,UpdateProfileApiView,UsernameCheckView,
UserSignupValidationView,UsernameValidationView,UserProfileApiView,SavedPostsApiView,
CustomTokenObtainPairView, CustomTokenRefreshView,PasswordResetApi,
PasswordResetConfirmApi,CustomUsersListApiView,ReportUserCreateApiView,
DeleteAccountAPIView,CheckLoginStatusAPIView,UserSearchView,delete_account,AccessTokenLoginView,
BlockUserView,UnblockUserView,ReportReasonsListAPIView,SavedTweetsMediaListView,SavedTweetsTextListView,
BlockedUsersListView,AppleLogin,GoogleLogin,ChangeUsernameView,ChangePasswordView,AddBonusApiview,ChangePasswordFLUsersView
)
from dj_rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)

urlpatterns = [
    path('add-bonus/', AddBonusApiview.as_view(), name='add-bonus'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/update/username/', ChangeUsernameView.as_view(), name='change_username'),
    path(
        'socialaccounts/',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    path(
        'socialaccounts/<int:pk>/disconnect/',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    ),
    path('social/apple/', AppleLogin.as_view(), name='ap_login'),
   path(
        'social/google/',
        GoogleLogin.as_view(),
         name='google_login'
    ),

    path('user/saved/photo-video/<int:user_id>/', SavedTweetsMediaListView.as_view(), name='user-saved'),
    path('user/saved/text/<int:user_id>/', SavedTweetsTextListView.as_view(), name='user-saved'),
    
    path('block/<int:user_id>/', BlockUserView.as_view(), name='block-user'),
    path('unblock/<int:user_id>/', UnblockUserView.as_view(), name='unblock-user'),
    path('blocked-users/<int:user_id>/', BlockedUsersListView.as_view(), name='blocked-users-list'),


    path('web-login/', AccessTokenLoginView.as_view(), name='token_obtain_pair'),
    
    path('delete-account/', delete_account, name='delete_account'),
    path('search/<str:query>/', UserSearchView.as_view(), name='user-search-by-username'),
    path('check-login/', CheckLoginStatusAPIView.as_view(), name='check-login-status'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('users/list/', CustomUsersListApiView.as_view(), name='users-list'),
    
    path('password-reset/', PasswordResetApi.as_view(), name='password_reset_api'),
    path('password-reset-fl/', ChangePasswordFLUsersView.as_view(), name='password_reset_api_fl'),
    path('password-reset-confirm/', PasswordResetConfirmApi.as_view(), name='reset_password_api'),


    path('login/',UserLoginView.as_view()),
    path("sign-up/", SignupConfirmationView.as_view(), name="signup"),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('delete/', DeleteAccountAPIView.as_view(), name='delete-account'),
    path('report/<int:user_id>/', ReportUserCreateApiView.as_view(), name='report-user'),
    path('report/reasons/list/', ReportReasonsListAPIView.as_view(), name='report-user'),

    path('profile/user/<int:id>/', UserProfileApiView.as_view(), name='user-profile'),
    path('profile/', ProfileApiView.as_view(), name='profile-detail'),
    path('profile/update/', UpdateProfileApiView.as_view(), name='profile-update'),
    path('user/saved/', SavedPostsApiView.as_view(), name='user-saved'),

    path('validate-user/', UserSignupValidationView.as_view(), name='validate-user'),
    path('validate-user-username/', UsernameValidationView.as_view(), name='validate-user-username'),
    path('login/check-username/', UsernameCheckView.as_view(), name='check-username'),

    # authentication/views.py
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    

]
