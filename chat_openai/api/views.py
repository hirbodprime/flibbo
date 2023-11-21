# django imports
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# rest imports
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat_openai.models import OpenAIChatInteraction,OpenAIAudioInteraction,OpenAIImageInteraction
from .serializers import (OpenAIChatInteractionSerializer,OpenAIAudioInteractionSerializer,
OpenAIImageInteractionSerializer,ChatInteractionSerializer,
 AudioInteractionSerializer, ImageInteractionSerializer)# python imports 
import tempfile
import os
import mimetypes

# open ai imports
# import openai
from openai import OpenAI

# Correct way to initialize the OpenAI client with your API key
client = OpenAI(
  api_key="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",
  organization="org-DEwPdQ2OtgPIlZSyhQJkBCGu"
)

class DeleteUserHistory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            OpenAIChatInteraction.objects.filter(user=user).delete()
            OpenAIAudioInteraction.objects.filter(user=user).delete()
            OpenAIImageInteraction.objects.filter(user=user).delete()

            return Response({"success":True,"message": "User history deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"success":False,"error": "Something happened While trying to delete your History"}, status=status.HTTP_204_NO_CONTENT)


class OpenAIChatInteractionView(CreateAPIView):
    queryset = OpenAIChatInteraction.objects.all()
    serializer_class = OpenAIChatInteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_prompt = self.request.data.get('user_text_prompt')
        user_chat_history = OpenAIChatInteraction.objects.filter(user=self.request.user)
        chat_history_messages = [
            {"role": "assistant", "content": chat.gpt_response} for chat in user_chat_history
        ]
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            *chat_history_messages,
            {"role": "user", "content": user_prompt}
        ]
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        # Extract GPT response message
        gpt_response = completion.choices[0].message.content  # Corrected line

        # Save model instance
        serializer.save(user=self.request.user, gpt_response=gpt_response)


class OpenAIAudioInteractionView(CreateAPIView):
    queryset = OpenAIAudioInteraction.objects.all()
    serializer_class = OpenAIAudioInteractionSerializer
    permission_classes = [IsAuthenticated]

    

    def perform_create(self, serializer):
        audio_file = self.request.data.get('user_audio_prompt')
        if not audio_file:
            return HttpResponseBadRequest("No audio file provided")

        file_name = audio_file.name.lower()
        if not self.is_supported_format(file_name):
            return HttpResponseBadRequest("Unsupported file format")

        mime_type, _ = mimetypes.guess_type(file_name)
        print("Original MIME Type:", mime_type)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            temp_file_path = tmp_file.name

        print("Temporary File Path:", temp_file_path)

        try:
            with open(temp_file_path, 'rb') as file:
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=file,
                    response_format="text"
                )
                gpt_response = transcript_response

            serializer.save(user=self.request.user, gpt_response=gpt_response)

        finally:
            os.remove(temp_file_path)



    def is_supported_format(self, file_name):
        supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
        return any(file_name.endswith('.' + fmt) for fmt in supported_formats)

 






# image_url = response.data[0].url

class OpenAIImageInteractionView(CreateAPIView):
    queryset = OpenAIImageInteraction.objects.all()
    serializer_class = OpenAIImageInteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        image_text = self.request.data.get('user_text_prompt_image')
        n_cout_str = self.request.data.get('n_cout', '1')  # default to 1 if not provided

        try:
            n_cout = int(n_cout_str)
        except ValueError:
            return Response({'error': 'Invalid value for n_cout'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=image_text,
                size="1024x1024",
                quality="standard",
                n=1,
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Dynamically build the save dictionary
        save_dict = {'user': self.request.user}
        for i in range(1):
            # Access each image URL in the response
            image_url = response.data[i].url
            save_dict[f'gpt_response{i + 1}'] = image_url

        serializer.save(**save_dict)


# open ai imports
# import openai

# # open ai keys
# openai.organization = "org-DEwPdQ2OtgPIlZSyhQJkBCGu"
# openai.api_key = "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"


# class OpenAIChatInteractionView(CreateAPIView):
#     queryset = OpenAIChatInteraction.objects.all()
#     serializer_class = OpenAIChatInteractionSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user_prompt = self.request.data.get('user_text_prompt')

#         # Call OpenAI API for GPT-4 completion
#         completion = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": user_prompt}
#             ]
#         )
        
#         gpt_response = completion.choices[0].message['content']
        
#         # Save model instance
#         serializer.save(user=self.request.user, gpt_response=gpt_response)






# class OpenAIAudioInteractionView(CreateAPIView):
#     queryset = OpenAIAudioInteraction.objects.all()
#     serializer_class = OpenAIAudioInteractionSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         audio_file = self.request.data.get('user_audio_prompt')
        
#         # Saving audio file temporarily to disk
#         # audio_path = default_storage.save('temp_audio.mp3', ContentFile(audio_file.read()))
    
#         transcript = openai.Audio.translate("whisper-1", audio_file)
#         transcript_text = transcript.get('text', '')

#         # Generate text with GPT-4 based on transcript
#         completion = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant. You do speech to text"},
#                 {"role": "user", "content": transcript_text}  # Use the extracted transcript
#             ]
#         )
        
#         gpt_response = completion.choices[0].message['content']
        
#         # Save model instance with user and GPT-4 response
#         serializer.save(user=self.request.user, gpt_response=gpt_response)















# class OpenAIImageInteractionView(CreateAPIView):
#     queryset = OpenAIImageInteraction.objects.all()
#     serializer_class = OpenAIImageInteractionSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         image_text = self.request.data.get('user_text_prompt_image')
#         n_cout_str = self.request.data.get('n_cout', '1')  # default to 1 if not provided

#         try:
#             n_cout = int(n_cout_str)
#         except ValueError:
#             return Response({'error': 'Invalid value for n_cout'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             response = openai.Image.create(
#                 prompt=image_text,
#                 n=n_cout,
#                 size="1024x1024"
#             )
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#         # Dynamically build the save dictionary
#         save_dict = {'user': self.request.user}
#         for i in range(n_cout):
#             save_dict[f'gpt_response{i + 1}'] = response['data'][i]['url']

#         serializer.save(**save_dict)




from rest_framework.views import APIView
from rest_framework.response import Response

class InteractionListView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        chat_interactions = OpenAIChatInteraction.objects.none()
        audio_interactions = OpenAIAudioInteraction.objects.none()
        image_interactions = OpenAIImageInteraction.objects.none()

        if user.is_authenticated:
            chat_interactions = OpenAIChatInteraction.objects.filter(user=user).order_by('-created_at')
            audio_interactions = OpenAIAudioInteraction.objects.filter(user=user).order_by('-created_at')
            image_interactions = OpenAIImageInteraction.objects.filter(user=user).order_by('-created_at')

        chat_serializer = ChatInteractionSerializer(chat_interactions, many=True)
        audio_serializer = AudioInteractionSerializer(audio_interactions, many=True)
        image_serializer = ImageInteractionSerializer(image_interactions, many=True)

        response_data = {
            'chats': chat_serializer.data,
            'audios': audio_serializer.data,
            'images': image_serializer.data
        }

        return Response(response_data)