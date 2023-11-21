from django.core.management.base import BaseCommand
from posts.models import TweetPostModel

class Command(BaseCommand):
    help = 'Check all locations in TweetPostModel and empty if the value is "null"'

    def handle(self, *args, **kwargs):
        # Filter tweets where location is "null"
        tweets_with_null_location = TweetPostModel.objects.filter(location__exact="null")

        # Iterate through the queryset and set location to an empty string
        for tweet in tweets_with_null_location:
            tweet.location = ""
            tweet.save()

        self.stdout.write(self.style.SUCCESS(f'Updated {tweets_with_null_location.count()} tweet(s) with "null" locations.'))
