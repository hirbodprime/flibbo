import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q, Count

from accounts.models import BlockModel 
from category.models import UserFavoriteCategories
from .models import TweetPostModel, TweetCommentModel
from posts.api.serializers import TweetPostConsumerSerializer, TweetCommentWebSocketSerializer
from following_system.models import FollowModel

from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend

logger = logging.getLogger(__name__)
User = get_user_model()
import json
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)



    


class HomeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            user = await self.authenticate(self.scope['query_string'])
            logger.info(f"User {user} connected to HomeConsumer.")
            if user:
                self.scope['user'] = user
                self.room_group_name = 'home'

                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                # Accept connection
                await self.accept()

                # Fetch and send posts after successful connection
                posts = await self.get_category_posts(user)
                await self.send(text_data=json.dumps({
                    'type': 'initial_posts',
                    'posts': posts
                }, cls=CustomJSONEncoder))

            else:
                # Close connection if user is not authenticated
                await self.close()
        except Exception as e:
            logger.error(f"Error in connect method: {str(e)}")
            raise
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        
        if data['action'] == 'like_post':
            post_id = data['post_id']
            liked_count = await self.like_post(post_id, user)
            await self.send(text_data=json.dumps({
                'type': 'like_post',
                'post_id': post_id,
                'liked_count': liked_count
            }))
        elif data['action'] == 'get_comments':
            tweet_id = data['post_id']
            comments = await self.get_comments(tweet_id, user)
            await self.send(text_data=json.dumps({
                'type': 'comments',
                'comments': comments
            }))
        elif data['action'] == 'like_comment':
            comment_id = data['comment_id']
            like_result = await self.like_comment(comment_id, user)
            await self.send(text_data=json.dumps({
                'type': 'like_comment',
                'comment_id': comment_id,
                'like_result': like_result
            }))
        elif data['action'] == 'create_comment':
            comment_data = await self.create_comment(data, user)
            await self.send(text_data=json.dumps({
                'type': 'new_comment',
                'comment': comment_data
            }, cls=CustomJSONEncoder))

            # Broadcast new comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_new_comment',
                    'comment': comment_data
                }
            )
        elif data['action'] == 'follow_user':
            user_to_follow_id = data['user_id']
            follow_result = await self.follow_user(user_to_follow_id, user)
            await self.send(text_data=json.dumps({
                'type': 'follow_user',
                'user_id': user_to_follow_id,
                'follow_result': follow_result
            }))

        elif data['action'] == 'unfollow_user':
            user_to_unfollow_id = data['user_id']
            unfollow_result = await self.unfollow_user(user_to_unfollow_id, user)
            await self.send(text_data=json.dumps({
                'type': 'unfollow_user',
                'user_id': user_to_unfollow_id,
                'unfollow_result': unfollow_result
            }))

    @database_sync_to_async
    def follow_user(self, user_to_follow_id, user):
        try:
            # Get the user to follow
            user_to_follow = User.objects.get(id=user_to_follow_id)
            follow_instance, created = FollowModel.objects.get_or_create(user=user)
            if follow_instance.is_user_following(user_to_follow):
                return {'success': False, 'message': 'Already following this user'}
            follow_instance.follow(user_to_follow)
            # Broadcast the follow event to the group
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_follow_user',
                    'follower_id': user.id,
                    'followed_id': user_to_follow_id
                }
            )
            return {'success': True, 'message': 'Successfully followed the user'}
        except User.DoesNotExist:
            return {'success': False, 'message': 'User to follow does not exist'}

    @database_sync_to_async
    def unfollow_user(self, user_to_unfollow_id, user):
        try:
            user_to_unfollow = User.objects.get(id=user_to_unfollow_id)
            follow_instance = FollowModel.objects.get(user=user)
            if not follow_instance.is_user_following(user_to_unfollow):
                return {'success': False, 'message': 'Not following this user'}
            follow_instance.unfollow(user_to_unfollow)
            # Broadcast the unfollow event to the group
            self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_unfollow_user',
                    'unfollower_id': user.id,
                    'unfollowed_id': user_to_unfollow_id
                }
            )
            return {'success': True, 'message': 'Successfully unfollowed the user'}
        except User.DoesNotExist:
            return {'success': False, 'message': 'User to unfollow does not exist'}
        except FollowModel.DoesNotExist:
            return {'success': False, 'message': 'Follow relationship does not exist'}

    async def broadcast_follow_user(self, event):
        await self.send(text_data=json.dumps({
            'type': 'follow_user',
            'follower_id': event['follower_id'],
            'followed_id': event['followed_id']
        }))

    async def broadcast_unfollow_user(self, event):
        await self.send(text_data=json.dumps({
            'type': 'unfollow_user',
            'unfollower_id': event['unfollower_id'],
            'unfollowed_id': event['unfollowed_id']
        }))

    async def broadcast_new_comment(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'comment': event['comment']
        }, cls=CustomJSONEncoder))

    @database_sync_to_async
    def create_comment(self, data, user):
        post_id = data.get('post_id')
        text = data.get('text')

        try:
            post = TweetPostModel.objects.get(id=post_id)
            comment_data = {
                'post_id': post_id,  # Pass the post_id
                'user': user,  # Assuming the serializer needs the user object
                'text': text,
            }


            serializer_context = {
                'request': user
            }

            serializer = TweetCommentWebSocketSerializer(data=comment_data, context=serializer_context)
            if serializer.is_valid(raise_exception=True):
                comment = serializer.save()
                return serializer.data
        except TweetPostModel.DoesNotExist:
            raise serializers.ValidationError("The specified post does not exist")

        return {}



    @database_sync_to_async
    def get_comments(self, post_id, user):
        # Your logic to fetch comments
        block_obj, created = BlockModel.objects.get_or_create(user=user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        users_who_blocked_current_user, created = BlockModel.objects.get_or_create(user=user)
        blocked_by_users_obj = users_who_blocked_current_user.blocked_by.all()

        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj

        comments = TweetCommentModel.objects.exclude(user__in=blocked_users_combined).filter(post=post_id).annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')

        # Serialize the comments
        serializer_context = {
        'request': user
        }

        comment_data = [TweetCommentWebSocketSerializer(comment,context=serializer_context ).data for comment in comments]
        return comment_data           
    @database_sync_to_async
    def get_category_posts(self, user):
        block_obj, created = BlockModel.objects.get_or_create(user=user)
        
        # Get IDs of users blocked by the current user
        users_blocked_by_current_user_ids = block_obj.blocked_users.values_list('id', flat=True)
        
        # Get IDs of users who have blocked the current user
        users_who_blocked_current_user_ids = BlockModel.objects.filter(blocked_by=user).values_list('user_id', flat=True)
        
        # Combine the lists of IDs
        blocked_users_combined_ids = set(users_blocked_by_current_user_ids).union(set(users_who_blocked_current_user_ids))

        # Fetch user's favorite categories and filter tweets accordingly
        user_categorymodel_obj = UserFavoriteCategories.objects.get(user=user)
        categories = user_categorymodel_obj.favorite_categories.all()
        logger.info(f"categories {categories}")

        serializer_context = {
        'request': user
        }

        tweets = TweetPostModel.objects.exclude(user_id__in=blocked_users_combined_ids).filter(
            category__in=categories, hide=False
        ).order_by('-created_date')[:10]  # Simplified pagination for demo purposes

        # Pass the custom context when instantiating the serializer
        tweet_data = [TweetPostConsumerSerializer(tweet, context=serializer_context).data for tweet in tweets]
        return tweet_data

    
    @database_sync_to_async
    def authenticate(self, query_string):
        # Extract token from query string and authenticate user
        token = dict(x.split('=') for x in query_string.decode().split("&")).get("token", None)
        if not token:
            return None
        try:
            # Decode token
            decoded_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
            # Get user from token
            user = get_user_model().objects.get(id=decoded_data['user_id'])
            return user
        except (InvalidToken, TokenError, get_user_model().DoesNotExist) as e:
            logger.error(f'Error in WebSocket token authentication: {e}')
            return None
    
    @database_sync_to_async
    def like_post_logic(self, post_id, user):
        try:
            tweet = TweetPostModel.objects.get(id=post_id)
            if user in tweet.likes.all():
                tweet.likes.remove(user)
                action = 'unliked'
            else:
                tweet.likes.add(user)
                action = 'liked'
            tweet.save()
            return {'count': tweet.likes.count(), 'action': action}
        except TweetPostModel.DoesNotExist:
            return {'count': 0, 'action': 'error'}

    async def like_post(self, post_id, user):
        # existing logic to like a post
        liked_count = await self.like_post_logic(post_id, user)
        # Broadcast the update to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_like_post',
                'post_id': post_id,
                'liked_count': liked_count
            }
        )
    
    async def broadcast_like_post(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'like_post',
            'post_id': event['post_id'],
            'liked_count': event['liked_count']
        }))
    @database_sync_to_async
    def like_comment_logic(self, comment_id, user):
        try:
            comment = TweetCommentModel.objects.get(id=comment_id)
            if user in comment.likes.all():
                comment.likes.remove(user)
                action = 'unliked'
            else:
                comment.likes.add(user)
                action = 'liked'
            comment.save()
            return {'count': comment.likes.count(), 'action': action}
        except TweetCommentModel.DoesNotExist:
            return {'count': 0, 'action': 'error'}
    async def like_comment(self, comment_id, user):
        # existing logic to like a comment
        like_result = await self.like_comment_logic(comment_id, user)
        # Broadcast the update to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_like_comment',
                'comment_id': comment_id,
                'like_result': like_result
            }
        )

    async def broadcast_like_comment(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'like_comment',
            'comment_id':   ['comment_id'],
            'like_result': event['like_result']
        }))








