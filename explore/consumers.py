from rest_framework import status
from django.db.models import Count
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import django
django.setup()




from posts.models import TweetPostModel  # Import your TweetPostModel
from explore.api.serializers import TweetPostSerializer  # Import your TweetPostSerializer
from .custom_pagination import CustomPagination  # Import your CustomPagination

class ExploreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({'message': 'you have been disconnected from the server'}))

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            username = text_data_json['username']

            # Now, let's fetch and send the tweets for the specified username
            tweet_data = await self.get_tweets(username)

            # You can send the tweet data back to the WebSocket client
            await self.send(text_data=json.dumps({'message': 'Tweets', 'data': tweet_data}))

        except json.JSONDecodeError:
            # Handle JSON decode error
            pass
        except Exception as e:
            # Handle other exceptions
            print(e)
            pass

    @database_sync_to_async
    def get_tweets(self, username):
        try:
            # Querying tweets for the specified username ordered by view count and creation date
            tweets = TweetPostModel.objects.filter(
                user__username=username,
                hide=False
            ).annotate(
                view_count=Count('viewed_by_users')
            ).order_by('-view_count', '-created_date')

            # Use only select_related() or prefetch_related() as needed
            tweets = tweets.select_related('user').prefetch_related('category')

            # Pagination
            paginator = CustomPagination()
            paginated_tweets = paginator.paginate_queryset(tweets, None)

            if not paginated_tweets:
                return {'success': True, 'data': 'No tweets available for this user'}

            # Bulk serialization
            tweet_data = TweetPostSerializer(paginated_tweets, many=True).data

            # Building response
            response_data = {
                "tweets": tweet_data,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }

            return {'success': True, 'data': response_data}

        except Exception as e:
            return {'success': False, 'error': str(e)}