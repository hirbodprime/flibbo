# your_app/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flibbo.settings')

from posts.models import TweetPostModel
from posts.api.serializers import TweetPostSerializer
from django.db.models import Count
from channels.db import database_sync_to_async

class ExploreConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        sort_by = data.get('sort_by', 'recent').lower()
        tweets = await self.get_tweets(sort_by)
        await self.send(text_data=json.dumps({
            'tweets': tweets
        }))

    @database_sync_to_async
    def get_tweets(self, sort_by):
        tweets = TweetPostModel.objects.filter(user__private=False, hide=False)

        if sort_by == 'popular':
            tweets = tweets.annotate(
                like_count=Count('likes'),
                view_count=Count('viewed_by_users')
            ).order_by('-like_count', '-view_count')
        elif sort_by == 'recent':
            tweets = tweets.order_by('-created_date')
        elif sort_by == 'views':
            tweets = tweets.annotate(
                view_count=Count('viewed_by_users')
            ).order_by('-view_count')
        else:
            # Handle invalid sort parameter
            return {'success': False, 'error': 'Invalid sort parameter'}

        tweets = tweets.select_related('user').prefetch_related('category')

        # Serialize the tweets
        tweet_data = TweetPostSerializer(tweets, many=True).data
        return {'success': True, 'data': tweet_data}

