# consumers.py

import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Activity
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend

logger = logging.getLogger(__name__)
User = get_user_model()

class ActivityConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = await self.authenticate(self.scope['query_string'])
        if user:
            self.scope['user'] = user
            print(user.id)
            self.room_group_name = f"group_activity_updates_{user.id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.send_user_activities(user)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_user_activities(self, user):
        activities = await self.get_user_activities(user)
        for activity in activities:
            await self.send_json(activity)

    @database_sync_to_async
    def get_user_activities(self, user):
        return list(Activity.objects.filter(user=user).values())

    async def activity_update(self, event):
        await self.send_json(event)

    @staticmethod
    @database_sync_to_async
    def authenticate(query_string):
        params = dict(x.split('=') for x in query_string.decode().split("&"))
        token = params.get("token", None)
        if not token:
            return None
        try:
            decoded_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
            return User.objects.get(id=decoded_data['user_id'])
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None
