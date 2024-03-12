from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import RequestToFollow,FollowModel
from activity.models import Activity

User = get_user_model()

@receiver(post_save, sender=RequestToFollow)
def request_to_follow_updated(sender, instance, **kwargs):
    print(instance.request_sender.id)
    if instance.status == 'ACCEPTED':
        print('ak')
        user_id = instance.requset_reciever.id
        # Get the user to follow
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

        # Get the instance of the user creating the follow
        user_creating_follow = instance.request_sender

        # Check if the user is already following
        user_creating_follow_followmodel, created = FollowModel.objects.get_or_create(user=user_creating_follow)
        if user_creating_follow_followmodel.is_user_following(user_to_follow):
            pass
        else:
            # Call the follow method
            # Activity.objects.create(user=user_creating_follow, followed_user=user_to_follow, activity_type=Activity.FOLLOW)
            user_creating_follow.increment_followings_count()
            user_creating_follow_followmodel.follow(user_to_follow)
            user_to_follow.increment_followers_count()
            # instance.delete()
            return {'success': True, 'follow': 'Successfully followed this user'}
    elif instance.status == 'PENDING':
        user_id = instance.requset_reciever.id
        # Get the user to follow
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

        # Get the instance of the user creating the follow
        user_creating_follow = instance.request_sender

        # Check if the user is already following
        Activity.objects.create(user=user_creating_follow, followed_user=user_to_follow, activity_type=Activity.FOLLOW)
    elif instance.status == 'REJECTED':
        instance.delete()
