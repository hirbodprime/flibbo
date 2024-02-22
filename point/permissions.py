from rest_framework import permissions
from .models import UserWalletModel

class HasValidWallet(permissions.BasePermission):
    message = 'You do not have a valid wallet.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user_wallet = UserWalletModel.objects.filter(user=request.user, wallet__isnull=False).first()
        return user_wallet and user_wallet.wallet is not None
