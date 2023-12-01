from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    message_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.message_sender.username} sent message to {self.message_receiver.username}'
