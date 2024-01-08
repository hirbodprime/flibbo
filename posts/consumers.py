from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import TweetPostModel
from channels.generic.websocket import AsyncWebsocketConsumer

class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'like_updates'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        tweet_id = data['tweet_id']
        user_id = data['user_id']
        print(tweet_id,user_id)
        # Process the like action
        liked = await self.update_like(tweet_id, user_id)

        # Broadcast the updated like count
        if liked is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'like_update',
                    'tweet_id': tweet_id,
                    'updated_like_count': liked,
                }
            )

    async def like_update(self, event):
        tweet_id = event['tweet_id']
        updated_like_count = event['updated_like_count']
        
        # Send the updated like count to WebSocket
        await self.send(text_data=json.dumps({
            'tweet_id': tweet_id,
            'updated_like_count': updated_like_count,
        }))

    @database_sync_to_async
    def update_like(self, tweet_id, user_id):
        try:
            tweet = TweetPostModel.objects.get(id=tweet_id)
            user = get_user_model().objects.get(id=user_id)
            if user in tweet.likes.all():
                print("i am here")
                tweet.likes.remove(user)
            else:
                print("i am here2")
                tweet.likes.add(user)
            return tweet.likes.count()
        except TweetPostModel.DoesNotExist:
            return None
