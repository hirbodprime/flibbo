from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from category.models import  UserFavoriteCategories, CategoryModel

class Command(BaseCommand):
    help = 'Create UserFavoriteCategories objects for all existing users and add all available categories to their favorites.'

    def handle(self, *args, **options):
        for user in CustomUser.objects.all():
            # Create UserFavoriteCategories object for the user
            user_favorite_categories,created = UserFavoriteCategories.objects.get_or_create(user=user)

            # Add all available categories to the favorite categories of the user
            all_categories = CategoryModel.objects.all()
            user_favorite_categories.favorite_categories.set(all_categories)

        self.stdout.write(self.style.SUCCESS('Successfully created UserFavoriteCategories objects for all users.'))
