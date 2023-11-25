from django.core.management.base import BaseCommand
from accounts.models import CustomUser  # Replace 'myapp' with the name of your app

class Command(BaseCommand):
    help = 'Converts all usernames to lowercase'

    def handle(self, *args, **kwargs):
        users = CustomUser.objects.all()
        for user in users:
            if user.username and user.username != user.username.lower():
                user.username = user.username.lower()
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated username for: {user.email}'))
            else:
                self.stdout.write(f'No update needed for: {user.email}')
