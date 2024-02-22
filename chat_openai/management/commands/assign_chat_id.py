from django.core.management.base import BaseCommand
from chat_openai.chat_id import generate_chat_id
from django.core.management.base import BaseCommand
from  chat_openai.models import OpenAIChatInteraction, OpenAIAudioInteraction, OpenAIImageInteraction, OpenAITextToSpeechInteraction, OpenAIChatID

class Command(BaseCommand):
    help = 'Assigns a single chat ID to all OpenAI interaction instances of each user'

    def handle(self, *args, **kwargs):
        # Call the function for each model
        self.assign_chat_id(OpenAIChatInteraction)
        self.assign_chat_id(OpenAIAudioInteraction)
        self.assign_chat_id(OpenAIImageInteraction)
        self.assign_chat_id(OpenAITextToSpeechInteraction)

    def assign_chat_id(self, model):
        interactions_without_chat = model.objects.filter(chat__isnull=True)
        user_chat_map = {}  # Mapping of users to their chat_id
        count = 0  # Counter for interactions updated

        for interaction in interactions_without_chat:
            user = interaction.user

            if user not in user_chat_map:
                # If this user doesn't have a chat_id yet, generate and store it
                unique_chat_id = generate_chat_id()
                chat_id_instance = OpenAIChatID.objects.create(
                    user=user,
                    chat_id=unique_chat_id
                )
                user_chat_map[user] = chat_id_instance
            else:
                # Use the existing chat_id for this user
                chat_id_instance = user_chat_map[user]

            # Assign the chat ID to the interaction and save
            interaction.chat = chat_id_instance
            interaction.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully assigned chat ID to {count} {model.__name__} interactions.'
        ))


# class Command(BaseCommand):
#     help = 'Assigns a single chat ID to all OpenAIChatInteraction instances of each user'

#     def handle(self, *args, **kwargs):
#         interactions_without_chat = OpenAIChatInteraction.objects.filter(chat__isnull=True)
#         user_chat_map = {}  # Mapping of users to their chat_id
#         count = 0  # Counter for interactions updated

#         for interaction in interactions_without_chat:
#             user = interaction.user

#             if user not in user_chat_map:
#                 # If this user doesn't have a chat_id yet, generate and store it
#                 unique_chat_id = generate_chat_id()
#                 chat_id_instance = OpenAIChatID.objects.create(
#                     user=user,
#                     chat_id=unique_chat_id
#                 )
#                 user_chat_map[user] = chat_id_instance
#             else:
#                 # Use the existing chat_id for this user
#                 chat_id_instance = user_chat_map[user]

#             # Assign the chat ID to the interaction and save
#             interaction.chat = chat_id_instance
#             interaction.save()
#             count += 1

#         self.stdout.write(self.style.SUCCESS(
#             f'Successfully assigned chat ID to {count} interactions.'
#         ))
