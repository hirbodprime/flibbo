# signals.py 
# Define a custom signalimport django

from django.dispatch import Signal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ReferralCodeModel
from .point_functionality import  process_referral_signup

User = get_user_model()

# @receiver(post_save, sender=User)
# def create_referral_code(sender, instance, created, **kwargs):
#     if created:
        
#         # Create ReferralCodeModel instance and assign it to a variable
#         referral_code_obj = ReferralCodeModel.objects.get(user=instance)

#         # Send the custom signal with the correct referral code
#         print("calling function")
#         process_referral_signup(
#             new_user=instance, 
#             referral_code=referral_code_obj.ref_code
#         )
