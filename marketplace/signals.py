from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NftProductModel
from wallet.models import UsersNfts

# @receiver(post_save, sender=NftProductModel)
# def create_usersnfts_entry(sender, instance, created, **kwargs):
#     if created:
        # instance.bought_or_not = True
        # instance.save()
        # UsersNfts.objects.create(user=instance.user, nft_product=instance, bought_or_not=True)


