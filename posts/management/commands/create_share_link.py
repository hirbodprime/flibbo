from django.core.management.base import BaseCommand
from posts.models import TweetPostModel

class Command(BaseCommand):
    help = 'create share link for all posts in TweetPostModel'

    def handle(self, *args, **kwargs):
        for tweet_post in TweetPostModel.objects.all():
            try:
                if not tweet_post.share_post:
                    from firebase_dynamic_links import dynamic_link_builder
                    builder = dynamic_link_builder(api_key='AIzaSyBq77V9pbQXFDoM-eOK5G67NB6GxvXXBcc')
                    options = {
                        'link': f'https://flibbo.com/share?post={tweet_post.id}',
                        'apn': 'com.flibbo.app', 
                        'ibi': 'com.flibbo.app'
                    }
                    short_link = builder.generate_short_link(app_code='flibbo', **options)
                    tweet_post.share_post = short_link
                    tweet_post.save()
                    self.stdout.write(self.style.SUCCESS(f'Compressed photo for tweet post {tweet_post.id}'))

            except IOError:
                self.stdout.write(self.style.ERROR(f'Error processing photo for tweet post {tweet_post.id}'))
