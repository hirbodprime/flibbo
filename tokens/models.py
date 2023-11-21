from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
