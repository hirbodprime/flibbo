from django.urls import path
from .views import NormalUsersListAPIView,WithDrawalRequestCreateView, UserWalletCreateView, UserAggregatedDataView, GoldUsersListAPIView

urlpatterns = [
    path('user/data/', UserAggregatedDataView.as_view(), name='user-aggregated-data'),
    path('add-wallet/', UserWalletCreateView.as_view(), name='withdrawal-requests'),
    path('withdrawal-requests/', WithDrawalRequestCreateView.as_view(), name='withdrawal-requests'),
    path('gold-users/<int:level>/', GoldUsersListAPIView.as_view(), name='gold-users-level'),
    path('normal-users/', NormalUsersListAPIView.as_view(), name='normal-users-list'),

]   
