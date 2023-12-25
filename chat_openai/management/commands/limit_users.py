from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from chat_openai.models import  UserAIStudioLimit

class Command(BaseCommand):
    help = 'Limit Users for AI Studio'

    def handle(self, *args, **options):
        for user in CustomUser.objects.all():
            # Create UserFavoriteCategories object for the user
            limit_user_obj,created = UserAIStudioLimit.objects.get_or_create(user=user)

            self.stdout.write(self.style.SUCCESS(f'Successfully limited user {limit_user_obj}'))
