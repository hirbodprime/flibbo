from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Activity

@receiver(post_save, sender=Activity)
def activity_post_save(sender, instance, created, **kwargs):
    if created:
        newest_activity = Activity.objects.filter(user=instance.user).order_by('-created_at').first()
        print(newest_activity.tweet.user.id)
        group_name = f"group_activity_updates_{newest_activity.tweet.user.id}"
        message = {
            'type': 'activity_update',
            'activity_id': instance.id,
            'activity_type': instance.activity_type,
            'sender':instance.user.username,
            'reciever':newest_activity.tweet.user.username,
            'related_post':newest_activity.tweet.id
            # Include other relevant activity info
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message)
