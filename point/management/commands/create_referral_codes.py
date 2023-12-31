# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from point.models import ReferralCodeModel

# User = get_user_model()

# class Command(BaseCommand):
#     help = 'Generate referral codes for all users'

#     def handle(self, *args, **kwargs):
#         users_without_referral = User.objects.filter(referralcodemodel__isnull=True)
#         for user in users_without_referral:
#             ReferralCodeModel.objects.create(user=user)
#             self.stdout.write(self.style.SUCCESS(f'Referral code created for {user.username}'))
