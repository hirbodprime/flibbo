from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class UserDeviceModel(models.Model):
    # Custom fields to mimic the FCMDevice model
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    user_token = models.TextField(null=True,blank=True)
    device_type = models.CharField(max_length=10, choices=(('web', 'web'), ('ios', 'ios'), ('android', 'android')),null=True,blank=True)
    user_ip = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"

    def __str__(self):
        return f"{self.user}"

    def send_message(self, title, body):
        # Implement your custom logic for sending messages
        pass
