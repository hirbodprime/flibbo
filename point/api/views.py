from django.shortcuts import render
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView,CreateAPIView
from rest_framework.views import APIView

from point.permissions import HasValidWallet
from .serializers import UserSerializer,WithDrawalRequestGetSerializer, WithDrawalRequestSerializer, UserWalletCreateSerializer, UserWalletSerializer, ReferralCodeSerializer, PointWalletSerializer, RefMoneySerializer
from point.models import WithDrawalRequestModel, RefMoneyModel, UserWalletModel, ReferralCodeModel, PointWalletModel, GoldUsersListModel


User = get_user_model()
dev_url = "dev.flxdevpanel.com"
app_url = "app.flxdevpanel.com"


class GoldUsersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, level, *args, **kwargs):
        if level not in [1, 2, 3]:
            return Response({'error': 'Invalid level'}, status=400)

        try:
            gold_users_list = GoldUsersListModel.objects.get(user=request.user)
        except GoldUsersListModel.DoesNotExist:
            return Response({'error': 'Gold users list not found'}, status=404)

        # Extract sort_by and username parameters from URL
        sort_by = request.query_params.get('sort_by', '')
        username = request.query_params.get('username', '')

        # Get queryset based on level
        users_qs = getattr(gold_users_list, f'level_{level}').all()

        # Filter by username if provided
        if username:
            users_qs = users_qs.filter(Q(username__icontains=username))

        # Apply sorting based on sort_by parameter
        if sort_by == 'ascending':
            users_qs = users_qs.order_by('join_date')
        elif sort_by == 'descending':
            users_qs = users_qs.order_by('-join_date')

        serializer = UserSerializer(users_qs, many=True)
        response_data = {
            'users': serializer.data
        }
        return Response(response_data)


# class GoldUsersListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, level, *args, **kwargs):
#         if level not in [1, 2, 3]:
#             return Response({'error': 'Invalid level'}, status=400)

#         try:
#             gold_users_list = GoldUsersListModel.objects.get(user=request.user)
#         except GoldUsersListModel.DoesNotExist:
#             return Response({'error': 'Gold users list not found'}, status=404)

#         # Extract sort_by parameter from URL
#         sort_by = request.query_params.get('sort_by', '')

#         # Get queryset based on level
#         users_qs = getattr(gold_users_list, f'level_{level}').all()

#         # Apply sorting based on sort_by parameter
#         if sort_by == 'ascending':
#             users_qs = users_qs.order_by('join_date')
#         elif sort_by == 'descending':
#             users_qs = users_qs.order_by('-join_date')

#         serializer = UserSerializer(users_qs, many=True)
#         response_data = {
#             'users': serializer.data
#         }
#         return Response(response_data)



class UserAggregatedDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile_image_url = f"https://{dev_url}{user.profile_image.url}" if user.profile_image else None
        
        user_wallet = UserWalletModel.objects.filter(user=user).first()
        user_wallet_data = UserWalletSerializer(user_wallet).data if user_wallet else None

        # Extract only the 'wallet' value from the serialized data
        wallet = user_wallet_data.get('wallet') if user_wallet_data else None

        user_points = PointWalletModel.objects.filter(user=user)
        referral_codes = ReferralCodeModel.objects.filter(user=user)
        withdrawal_requests = WithDrawalRequestModel.objects.filter(user=user)
        ref_money = RefMoneyModel.objects.filter(for_user=user)

        points_data = PointWalletSerializer(user_points, many=True).data
        referral_codes_data = ReferralCodeSerializer(referral_codes, many=True).data
        withdrawal_requests_data = WithDrawalRequestGetSerializer(withdrawal_requests, many=True).data
        ref_money_data = RefMoneySerializer(ref_money, many=True).data

        gold_user_record = GoldUsersListModel.objects.filter(user=user).first()

        # Function to get first 3 users' profile images
        def get_first_three_users_images(users_qs):
            return [
                f"https://{dev_url}{user.profile_image.url}" if user.profile_image else None
                for user in users_qs.all()[:3]
            ]

        # Initialize counts and images
        level_1_count = level_2_count = level_3_count = 0
        level_1_images = level_2_images = level_3_images = []

        if gold_user_record:
            # Fetch counts
            level_1_count = gold_user_record.level_1.count()
            level_2_count = gold_user_record.level_2.count()
            level_3_count = gold_user_record.level_3.count()

            # Fetch images
            level_1_images = get_first_three_users_images(gold_user_record.level_1)
            level_2_images = get_first_three_users_images(gold_user_record.level_2)
            level_3_images = get_first_three_users_images(gold_user_record.level_3)

        gold_data = {
            'gold_users_level_1_count': level_1_count,
            'gold_users_level_1_images': level_1_images,
            'gold_users_level_2_count': level_2_count,
            'gold_users_level_2_images': level_2_images,
            'gold_users_level_3_count': level_3_count,
            'gold_users_level_3_images': level_3_images
        }

        enriched_ref_money_data = []

        for item in ref_money_data:
            user_id = item['user']
            ref_user_instance = User.objects.get(id=user_id)

            # Add the username and profile image to each item
            item['username'] = ref_user_instance.username
            item['profile_image'] = f"https://{dev_url}{ref_user_instance.profile_image.url}" if ref_user_instance.profile_image else None

            enriched_ref_money_data.append(item)
        return Response({
            'points': points_data[0]['balance'] if points_data else 0.0,
            'referral_code': referral_codes_data[0]['ref_code'] if referral_codes_data else None,
            'user_wallet': wallet,
            'users': gold_data,
            'withdrawal_requests': withdrawal_requests_data,
            'ref_money': enriched_ref_money_data,
            'profile_image': profile_image_url 
        })

class UserWalletCreateView(CreateAPIView):
    serializer_class = UserWalletCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        wallet_address = serializer.validated_data.get('wallet')
        if not wallet_address:
            raise ValidationError("A wallet address must be provided to create or update a wallet.")

        # Check if the user already has a wallet
        user_wallet = UserWalletModel.objects.filter(user=self.request.user).first()

        if user_wallet:
            # Update the existing wallet
            user_wallet.wallet = wallet_address
            user_wallet.save()
        else:
            # Create a new wallet for the user
            serializer.save(user=self.request.user)

class WithDrawalRequestCreateView(CreateAPIView): 
    serializer_class = WithDrawalRequestSerializer
    permission_classes = [IsAuthenticated, HasValidWallet]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Set the user to the current user


