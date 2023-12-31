from django.db import models
from django.contrib.auth import get_user_model
import random
import string
User = get_user_model()

class ReferralCodeModel(models.Model):
    user = models.ForeignKey(User, related_name='referral_codes', on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=8)
    referrer = models.ForeignKey(User, related_name='referred_by', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ref_code:
            # Generate a random string of letters and digits
            self.ref_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        super(ReferralCodeModel, self).save(*args, **kwargs)

class PointWalletModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

class GoldUsersListModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level_1 = models.ManyToManyField(User, related_name='gold_users_level_1',blank=True)
    level_2 = models.ManyToManyField(User, related_name='gold_users_level_2',blank=True)
    level_3 = models.ManyToManyField(User, related_name='gold_users_level_3',blank=True)
    
class NormalUsersListModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='users_normal')

transaction_status=(
    ('Pending','Pending'),
    ('Failed','Failed'),
    ('Success','Success'),
    )

class WithDrawalRequestModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=transaction_status)
    status_failed = models.TextField()


