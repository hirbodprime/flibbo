from django.db.models.signals import pre_save , m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CustomUser, OldUsername, ReportUser
from datetime import timedelta
from category.models import UserFavoriteCategories,CategoryModel

from accounts.models import AccessToken
import uuid  # For generating unique tokens

@receiver(pre_save, sender=CustomUser)
def replace_username_spaces_with_dashes(sender, instance, **kwargs):
    if instance.username: 
        if ' ' in instance.username:
            instance.username = instance.username.replace(' ', '')
        if '@' in instance.username:
            instance.username = instance.username.replace('@', '')
        if '#' in instance.username:
            instance.username = instance.username.replace('#', '')
        instance.username = instance.username.lower()



@receiver(post_save, sender=CustomUser)
def create_access_token(sender, instance, created, **kwargs):
    if created:
        token = uuid.uuid4().hex  # Generate a unique token
        AccessToken.objects.create(user=instance, token=token)

@receiver(post_save, sender=CustomUser)
def create_user_favorite_categories(sender, instance, created, **kwargs):
    if created:
        # Create UserFavoriteCategories object for the user
        user_favorite_categories = UserFavoriteCategories.objects.create(user=instance)
        
        # Add all available categories to the favorite categories of the user
        all_categories = CategoryModel.objects.all()
        user_favorite_categories.favorite_categories.set(all_categories)
        
        # Add all available subcategories to the favorite subcategories of the user

@receiver(m2m_changed, sender=ReportUser.reported_by.through)
def check_reports_count(sender, instance, **kwargs):
    if instance.report_count >= 200:
        # Code to ban the user for 1 week
        user_to_ban = instance.user
        user_to_ban.is_active = False
        user_to_ban.save()
        unban_time = timezone.now() + timedelta(weeks=1)
        instance.unban_time = unban_time
        instance.save()




@receiver(pre_save, sender=CustomUser)
def record_username_change(sender, instance, **kwargs):
    try:
        previous_instance = CustomUser.objects.get(pk=instance.pk)
        if instance.username != previous_instance.username:
            expiration_date = timezone.now() + timezone.timedelta(days=15)
            OldUsername.objects.create(user=instance, old_username=previous_instance.username, expiration_date=expiration_date)
            instance.last_username_change = timezone.now()
    except CustomUser.DoesNotExist:
        pass
