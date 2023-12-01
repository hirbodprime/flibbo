from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.user = self.scope["user"]
        # if self.user.is_authenticated:
        await self.accept()
        # else:
        #     await self.close()

    async def disconnect(self, close_code):
        await self.send(text_data=json.dumps({'message': 'you have been disconnected from the server'}))


    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            receiver_username = text_data_json['receiver']
            sender_username = text_data_json['sender']

            await self.save_message(sender_username,message, receiver_username)

        except json.JSONDecodeError:
            # Handle JSON decode error
            pass
        except Exception as e:
            # Handle other exceptions
            print(e)
            pass
    @database_sync_to_async
    def save_message(self, sender_username, message, receiver_username):
        User = get_user_model()
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)
        # Assuming you have a Message model as described earlier
        from .models import Message
        Message.objects.create(
            message_sender=sender,
            message_receiver=receiver,
            content=message
        )

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope["user"]
#         if self.user.is_authenticated:
#             await self.accept()
#         else:
#             await self.close()

#     async def disconnect(self, close_code):
#         await self.send(text_data=json.dumps({'message': 'you have been disconnected from the server'}))


#     async def receive(self, text_data):
#         if not self.user.is_authenticated:
#             await self.send(text_data=json.dumps({'error': 'You are not authenticated'}))
#             return

#         try:
#             text_data_json = json.loads(text_data)
#             message = text_data_json['message']
#             receiver_username = text_data_json['receiver']

#             await self.save_message(message, receiver_username)

#         except json.JSONDecodeError:
#             # Handle JSON decode error
#             pass
#         except Exception as e:
#             # Handle other exceptions
#             print(e)
#             pass
#     @database_sync_to_async
#     def save_message(self, message, receiver_username):
#         User = get_user_model()
#         sender = self.user  # Using the authenticated user
#         receiver = User.objects.get(username=receiver_username)
        
#         from .models import Message
#         Message.objects.create(
#             message_sender=sender,
#             message_receiver=receiver,
#             content=message
#         )