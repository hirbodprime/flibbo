from django.db import models
from django.contrib.auth import get_user_model
from marketplace.models import NftProductModel  

User = get_user_model()

class UsersNfts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_nfts')
    nft_product = models.ForeignKey(NftProductModel, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    bought_or_not = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    video = models.FileField(upload_to='nft_videos', blank=True, null=True)
    def __str__(self):
        return f"{self.user.username}'s NFT Purchase: {self.nft_product.title}"

    class Meta:
        verbose_name = 'User NFT Purchase'
        verbose_name_plural = 'User NFT Purchases'
