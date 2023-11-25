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

class WalletModel(models.Model):
    # Assuming each user has one wallet, link to the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')

    # Store the balance with decimal precision
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    # Optional: Store the date when the wallet was created
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional: Store the date when the wallet was last updated
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner}'s Wallet"

    # Optional: Add methods for deposit, withdraw, etc.
    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

