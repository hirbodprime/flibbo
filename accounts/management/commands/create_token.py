from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import AccessToken
import uuid  # For generating unique tokens
User = get_user_model()
class Command(BaseCommand):
    help = 'Create access tokens for users who do not have one.'

    def handle(self, *args, **kwargs):
        users_without_tokens = User.objects.filter(accesstoken__isnull=True)

        for user in users_without_tokens:
            # Generate a unique token (You can use any token generation logic here)
            token = uuid.uuid4().hex

            # Create AccessToken
            AccessToken.objects.create(user=user, token=token)

            self.stdout.write(self.style.SUCCESS(f'Successfully created access token for user {user.username}'))
