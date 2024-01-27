# django imports
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest , HttpResponse
from django.db.models import Q

# rest imports
from rest_framework.generics import CreateAPIView,GenericAPIView,ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response    
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from .history_serializers import * 
from chat_openai.models import HeyGenTalkingPhotoIDModel,HeyGenCreateVideoModel,SuggestPromptsImageModel,SuggestPromptsModel,OpenAIChatID,TalkImages,Dialect,Language,LanguageAndDialectRelation,TextToSpeechResponse,VoiceActorModel,FlikiVideoModel,UserAIStudioLimit,TextToImageResponse,StyleListModel,AIToolsModel,ClipResponse,AnimationResponse,TalkResponse,OpenAIChatInteraction,CategoriesModel,OpenAIAudioInteraction,OpenAIImageInteraction,OpenAITextToSpeechInteraction,OpenAIChatCategories
from .serializers import (HeyGenTalkingPhotoIDModelSerializer,HeyGenTalkingPhotoImageUploadSerializer,SuggestPromptsImageSerializer,TalkVoiceActorSerializer,OpenAIChatIDSerializer,TalkImagesListSerializer,VoiceActorSerializer,StylesModelSerializer,AIToolsModelSerializer,OpenAIChatInteractionSerializer,OpenAIAudioInteractionSerializer,
OpenAIImageInteractionSerializer,ChatInteractionSerializer,SuggestPromptsSerializer,
 AudioInteractionSerializer, ImageInteractionSerializer, OpenAICategoriesSerializer,OpenAIChatCategoriesSerializer, OpenAITextToSpeechInteractionSerializer,OpenAIChatCategoriesSerializer)
from explore.custom_pagination import CustomPagination
from chat_openai.studio_d import create_talk,get_animation,get_talk,create_animation,get_presenters,get_presenter_drivers,create_clip,get_clip
from chat_openai.fliki import generate_text_to_image,get_langunages,get_dialects,get_voices,get_status,create_video,generate_text_to_speech
# python imports 
import json
from datetime import datetime
import tempfile
import os
import mimetypes
from dotenv import load_dotenv
from openai import OpenAI
from chat_openai.chat_id import generate_chat_id
import logging
import random
from chat_openai.heygen import create_video_heygen,list_avatars, list_voices, get_video, add_caption, get_caption, get_langunages_translate, create_video_translate,get_video_translate
load_dotenv()
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  organization=os.getenv("OPENAI_ORG_API_KEY")
)




# heygen -----------------------------------------
class HeyGenGetVideoTranslateStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,video_id):
        status_data = get_video_translate(video_id)
        return Response(status_data)
class HeyGenCreateVideoCaptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, video_id):
        get_video_res = add_caption(video_id)
        return Response(get_video_res)

class HeyGenGetVideoCaptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, video_id):
        get_video_res = get_caption(video_id)
        return Response(get_video_res)


class HeyGenGetVideoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, video_id):
        get_video_res = get_video(video_id)
        return Response(get_video_res)

class HeyGenGetVoicesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        voice_list = list_voices()
        return Response(voice_list)

class HeyGenGetAvatarsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        avatars_list = list_avatars()
        return Response(avatars_list)
class HeyGenGetLanguagesListTranslateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        languages_list = get_langunages_translate()
        return Response(languages_list)
# create_video_translate



class HeyGenCreateVideoTranslateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user_limit, created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit <= 0:
            return Response({"error": "You are out of Energy"}, status=status.HTTP_400_BAD_REQUEST)

        video = request.FILES.get('video')
        if not video:
            return Response({"error": "video file is required."}, status=status.HTTP_400_BAD_REQUEST)
        video_path = default_storage.save('uploads/' + video.name, ContentFile(video.read()))
        video_url = settings.SITE_DOMAIN + settings.MEDIA_URL + video_path

        required_fields = ["video", "output_language"]
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({"error": f"{field} field is required and cannot be empty."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Call create_talk with validated data and image URL
        heygen_video_response = create_video_translate(
            video_url,
            request.data['output_language'],
            )
            
        try:
            if heygen_video_response["data"]["video_translate_id"]:
                # Save response data to model
                response_data = heygen_video_response["data"]
                HeyGenCreateVideoModel.objects.create(
                    user = request.user,
                    video_id=response_data['video_translate_id'],
                    voice_id=request.data['output_language'],

                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Video created successfully","data":response_data})
        except: 
            
            return Response({"message": f"Video Failed To create {heygen_video_response}"})
        # Handle error case
        return Response({"error": heygen_video_response.get("error", "Failed to create Video")},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class HeyGenListTalkingPhotoAPIView(ListAPIView):
    serializer_class = HeyGenTalkingPhotoIDModelSerializer

    def get_queryset(self):
        # Get the current user
        user = self.request.user
        # Return the queryset that contains HeyGenTalkingPhotoIDModel objects for this user
        return HeyGenTalkingPhotoIDModel.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

class HeyGenTalkingImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        import requests
        from chat_openai.heygen import api_key
        serializer = HeyGenTalkingPhotoImageUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            image_file = serializer.validated_data['image']

            # Send image to heygen.com
            try:
                with image_file.open('rb') as f:
                    resp = requests.post(
                        "https://upload.heygen.com/v1/talking_photo",
                        data=f,
                        headers={"Content-Type": "image/jpeg", "x-api-key": api_key}
                    )
                resp.raise_for_status()
                response_data = resp.json()
                # Save response in database
                HeyGenTalkingPhotoIDModel.objects.create(
                    user=request.user,
                    image_url=response_data['data']['talking_photo_url'],
                    image_id=response_data['data']['talking_photo_id']
                )

                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except requests.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HeyGenCreateVideoView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user_limit, created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit <= 0:
            return Response({"error": "You are out of Energy"}, status=status.HTTP_400_BAD_REQUEST)
        talking_photo_id = request.data.get('talking_photo_id', None)
        avatar_id = request.data.get('avatar_id', None)

        if not (talking_photo_id or avatar_id):
            return Response({"error": "Either 'talking_photo_id' or 'avatar_id' is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        audio = request.FILES.get('input_audio', None)
        input_text = request.data.get('input_text', '')

        if bool(audio) == bool(input_text):  # Checks if either both are provided or both are missing
            return Response({"error": "Either 'input_audio' or 'input_text' is required, but not both."},
                            status=status.HTTP_400_BAD_REQUEST)

        if audio:
            audio_path = default_storage.save('uploads/' + audio.name, ContentFile(audio.read()))
            audio_url = settings.SITE_DOMAIN + settings.MEDIA_URL + audio_path

        required_fields = ["bg_color", "ratio", "voice_id"]
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response({"error": f"{field} field is required and cannot be empty."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Call create_talk with validated data and image URL
        heygen_video_response = create_video_heygen(
            request.data['bg_color'],
            request.data['ratio'],
            avatar_id if avatar_id else None,
            input_text if input_text else None,
            audio_url if audio else None,
            request.data['voice_id'],
            talking_photo_id if talking_photo_id else None
        )
        print(heygen_video_response)
        try:
            if heygen_video_response["data"]["video_id"]:
                print("here")
                # Save response data to model
                response_data = heygen_video_response["data"]
                HeyGenCreateVideoModel.objects.create(
                    user=request.user,
                    video_id=response_data['video_id'],
                    background=request.data['bg_color'],
                    ratio=request.data['ratio'],
                    avatar_id=avatar_id,
                    talking_photo_id=talking_photo_id,
                    input_text=input_text if input_text else None,
                    input_audio=audio_url if audio else None,
                    voice_id=request.data['voice_id'],
                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": "Video created successfully", "data": response_data})
        except:
            return Response({"message": f"Video Failed To create {heygen_video_response}"})

        # Handle error case
        return Response({"error": heygen_video_response.get("error", "Failed to create Video")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserAllResponsesView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        talk_responses = TalkResponse.objects.filter(user=user).order_by('-created_at')
        clip_responses = ClipResponse.objects.filter(user=user).order_by('-created_at')
        animation_responses = AnimationResponse.objects.filter(user=user).order_by('-created_at')
        text_to_image_responses = TextToImageResponse.objects.filter(user=user).order_by('-created_at')
        text_to_speech_responses = TextToSpeechResponse.objects.filter(user=user).order_by('-created_at')
        fliki_video_responses = FlikiVideoModel.objects.filter(user=user).order_by('-created_at')

        talk_serializer = TalkResponseSerializer(talk_responses, many=True)
        clip_serializer = ClipResponseSerializer(clip_responses, many=True)
        animation_serializer = AnimationResponseSerializer(animation_responses, many=True)
        text_to_image_serializer = TextToImageResponseSerializer(text_to_image_responses, many=True)
        text_to_speech_serializer = TextToSpeechResponseSerializer(text_to_speech_responses, many=True)
        fliki_video_serializer = FlikiVideoModelSerializer(fliki_video_responses, many=True)

        combined_data = (talk_serializer.data + clip_serializer.data + 
                         animation_serializer.data + text_to_image_serializer.data +
                         text_to_speech_serializer.data + fliki_video_serializer.data)

        # Sort combined data by 'created_at' in descending order

        return Response(combined_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_random_prompts(request):
    prompts_count = SuggestPromptsModel.objects.count()
    random_indices = random.sample(range(prompts_count), min(3, prompts_count))
    random_prompts = [SuggestPromptsModel.objects.all()[idx] for idx in random_indices]
    serializer = SuggestPromptsSerializer(random_prompts, many=True)
    response_data = {
        'prompts':serializer.data
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_random_image_prompts(request):
    prompts_count = SuggestPromptsImageModel.objects.count()
    random_indices = random.sample(range(prompts_count), min(3, prompts_count))
    random_prompts = [SuggestPromptsImageModel.objects.all()[idx] for idx in random_indices]
    serializer = SuggestPromptsImageSerializer(random_prompts, many=True)
    response_data = {
        'prompts':serializer.data
    }
    return Response(response_data)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat(request, chat_id):
    """
    Function API View to delete a chat and its related interactions using GET method.
    """
    # Retrieve the chat and check if the request user is the owner
    chat = get_object_or_404(OpenAIChatID, chat_id=chat_id)

    if chat.user != request.user:
        # If the user is not the owner of the chat, deny the request
        return Response({'error': 'You do not have permission to delete this chat.'}, status=status.HTTP_403_FORBIDDEN)

    # Delete related objects
    OpenAIChatInteraction.objects.filter(chat=chat).delete()
    OpenAIAudioInteraction.objects.filter(chat=chat).delete()
    OpenAIImageInteraction.objects.filter(chat=chat).delete()
    OpenAITextToSpeechInteraction.objects.filter(chat=chat).delete()

    # Finally, delete the chat itself
    chat.delete()

    return Response({'message': 'Chat and related interactions deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class ChatInteractionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id=None):
        try:
            user = request.user
            if not chat_id:
                # Get the newest chat_id for the authenticated user
                latest_chat = OpenAIChatID.objects.filter(user=user).latest('created_at')
                chat_id = latest_chat.chat_id

            chat = OpenAIChatID.objects.get(chat_id=chat_id, user=user)
            chat_interactions = OpenAIChatInteraction.objects.filter(chat=chat)
            audio_interactions = OpenAIAudioInteraction.objects.filter(chat=chat)
            image_interactions = OpenAIImageInteraction.objects.filter(chat=chat)

            chat_serializer = OpenAIChatInteractionSerializer(chat_interactions, many=True)
            audio_serializer = OpenAIAudioInteractionSerializer(audio_interactions, many=True)
            image_serializer = OpenAIImageInteractionSerializer(image_interactions, many=True)

            return Response({
                'chat_id': chat_id,
                'chat_interactions': chat_serializer.data,
                'audio_interactions': audio_serializer.data,
                'image_interactions': image_serializer.data
            })
        except OpenAIChatID.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)



class OpenAIChatIDCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OpenAIChatIDSerializer
    

    def perform_create(self, serializer):
        # Ensure uniqueness of chat_id
        max_attempts = 10
        for _ in range(max_attempts):
            chat_id = generate_chat_id()
            if not OpenAIChatID.objects.filter(chat_id=chat_id).exists():
                # Set the user to the request user and save
                serializer.save(user=self.request.user, chat_id=chat_id)
                return
        # Handle the rare case where a unique chat_id is not found
        raise IntegrityError("Unable to generate a unique chat ID")


class OpenAIChatIDHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OpenAIChatIDSerializer

    def get_queryset(self):
        # Filter the queryset to only include records for the request user
        user = self.request.user
        return OpenAIChatID.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data})


class TalkVoiceActorListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = VoiceActorModel.objects.all()
    serializer_class = VoiceActorSerializer
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data})


class TalkImagesListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TalkImagesListSerializer
    queryset = TalkImages.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data})

class VoiceActorListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        language = request.query_params.get('language')
        gender = request.query_params.get('gender')
        
        if language and gender:
            voice_actors = VoiceActorModel.objects.filter(language=language, gender=gender)
        else:
            return Response({"error": "Language and gender parameters are required."}, status=400)

        serializer = VoiceActorSerializer(voice_actors, many=True)
        response_data = {
            'data':serializer.data
        }
        return Response(response_data)


class GetStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,video_id):
        status_data = get_status(video_id)
        return Response(status_data)

class GetVoicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, language=None, gender=None):
        # Check if language and gender are provided
        if not language:
            return Response({'error': 'Language ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not gender:
            return Response({'error': 'Gender ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve Language object or return 404
        obj = get_object_or_404(Language, name=language)

        # Retrieve LanguageAndDialectRelation object or return 404
        obj_relation = get_object_or_404(LanguageAndDialectRelation, language=obj)
        print(obj_relation.language._id, obj_relation.dialect._id)
        # Get voices data
        voice_data = get_voices(obj_relation.language._id, obj_relation.dialect._id, gender)
        return Response(voice_data)


class GetDialectsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        dialects_data = get_dialects()
        return Response(dialects_data)

class GetLanguagesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        languages_data = get_langunages()
        return Response(languages_data)

class StylesListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        style_list = StyleListModel.objects.all()
        serializer = StylesModelSerializer(style_list, many=True)
        return Response({'data': serializer.data})

class AIToolsListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        ai_tools = AIToolsModel.objects.all()
        serializer = AIToolsModelSerializer(ai_tools, many=True)
        return Response({'data': serializer.data,"limit":user_limit.limit})



class GetClipView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, clip_id):
        try:
            clip_response = ClipResponse.objects.get(clip_id=clip_id)
        except clip_response.DoesNotExist:
            return Response({"error": "Clip not found"}, status=status.HTTP_404_NOT_FOUND)

        clip_data = get_clip(clip_response.clip_id)
        return Response(clip_data)

class GetPresentersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, limit):
        presenters_data = get_presenters(limit)
        return Response(presenters_data)

class GetPresenterDriversView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, presenter_id):
        driver_data = get_presenter_drivers(presenter_id)
        return Response(driver_data)

class GetTalkView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, talk_id):
        try:
            talk_response = TalkResponse.objects.get(talk_id=talk_id)
        except TalkResponse.DoesNotExist:
            return Response({"error": "Talk not found"}, status=status.HTTP_404_NOT_FOUND)

        talk_data = get_talk(talk_response.talk_id)
        return Response(talk_data)

class GetAnimationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, animation_id):
        try:
            animation_response = AnimationResponse.objects.get(animation_id=animation_id)
            print(animation_response)
        except animation_response.DoesNotExist:
            return Response({"error": "Animation not found"}, status=status.HTTP_404_NOT_FOUND)

        animation_data = get_animation(animation_response.animation_id)
        return Response(animation_data)

class GetStatusVideoView(APIView):
    def post(self, request, *args, **kwargs):
        required_fields = ['video_id']
        for field in required_fields:
            if field not in request.data or not request.data[field]:
                return Response(
                    {"error": f"'{field}' field is required and cannot be empty."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        get_video_status = get_status(request.data['video_id'])
        print('get_video_status: ',get_video_status)  # or use logging

        if get_video_status['success'] == True:
            if get_video_status['data']['status'] == "processing":
                return Response({"message": "Video is Being Created",**get_video_status['data']})

            if get_video_status['data']['status'] == "success":
                fliki_obj = get_object_or_404(FlikiVideoModel, video_id=request.data['video_id'])
                fliki_obj.image_link = get_video_status['data']['file']
                fliki_obj.save()
                return Response({"message": f"Video created successfully",**get_video_status})

        # Handle error case
        return Response({"error":f"Failed to create video, reasone:  {get_video_status['error']['message']}",},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateVideoFlikiView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit > 0:

            required_fields = ['text_input', 'voice_id', 'aspectratio', 'bg_music']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(
                        {"error": f"'{field}' field is required and cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            create_video_res = create_video(
                request.data['text_input'],
                request.data['voice_id'],
                request.data['aspectratio'],
                request.data['bg_music'],
            )
            if create_video_res.get("success"):
                FlikiVideoModel.objects.create(
                    video_id = create_video_res['data']['data']['id'],
                    text_input=request.data['text_input'],
                    voice_id=request.data['voice_id'],
                    aspectratio=request.data['aspectratio'],
                    bg_music=request.data['bg_music'],
                    user=request.user
                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Video created successfully","data":create_video_res['data']['data']['id']})

            # Handle error case
            return Response({"error": create_video_res.get("error", "Failed to create video")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)

class CreateTextToSpeechView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit > 0:

            required_fields = ['text_input','voice_id']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(
                        {"error": f"'{field}' field is required and cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            text_to_speech = generate_text_to_speech(
                request.data['text_input'],
                request.data['voice_id'],
            )

            # Check if the operation was successful
            if text_to_speech.get("success") == True:
                response_data = text_to_speech["data"]
                TextToSpeechResponse.objects.create(
                    audio_link=response_data['data']['audio'],
                    text_input=request.data['text_input'],
                    voice_id=request.data['voice_id'],
                    user=request.user,
                    duration=response_data['data']['duration']
                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Video created successfully","data":response_data})

            # Handle error case
            return Response({"error": text_to_speech.get("error", "Failed to create video")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)
class CreateTextToImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        style_obj_id = get_object_or_404(StyleListModel,id=request.data['style_id'])
        if user_limit.limit > 0:
            required_fields = ['text_input','style_id']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(
                        {"error": f"'{field}' field is required and cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            text_to_image = generate_text_to_image(
                request.data['text_input'],
                style_obj_id.name2,
            )

            # Check if the operation was successful
            if text_to_image.get("success"):
                # Save response data to model
                print(text_to_image)
                response_data = text_to_image["data"]
                # print(response_data['data']['image'])
                
                TextToImageResponse.objects.create(
                    image_link=response_data['data']['image'],
                    text_input=request.data['text_input'],
                    style=style_obj_id,
                    user=request.user
                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Image created successfully","data":response_data})

            # Handle error case
            return Response({"error": animation_response.get("error", "Failed to create animation")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)


class CreateAnimationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Uncomment these lines if you're handling image uploads
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit > 0:

            image = request.FILES.get('image')
            if not image:
                return Response({"error": "Image file is required."}, status=status.HTTP_400_BAD_REQUEST)
            image_path = default_storage.save('uploads/' + image.name, ContentFile(image.read()))
            image_url = settings.SITE_DOMAIN + settings.MEDIA_URL + image_path
            # image_url = "https://dev.flxdevpanel.com/media/talk-images/big/Rectangle.png"
            animation_response = create_animation(
                image_url
            )
            # Check if the operation was successful
            if animation_response.get("success"):
                # Save response data to model
                print(animation_response)
                response_data = animation_response["data"]
                AnimationResponse.objects.create(
                    animation_id=response_data["id"],
                    created_at=datetime.fromisoformat(response_data["created_at"]),
                    created_by=response_data["created_by"],
                    object_type=response_data["object"],
                    status=response_data["status"],
                    user=request.user

                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Animation created successfully","data":response_data})

            # Handle error case
            return Response({"error": animation_response.get("error", "Failed to create animation")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)
class CreateClipView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # text_input,presenter_id,driver_id,bg_color
        # Validate other required fields
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit > 0:
            required_fields = ['text_input', 'presenter_id', 'driver_id', 'bg_color','subtitle', 'voice_id', 'provider_id', 'speed_rate']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(
                        {"error": f"'{field}' field is required and cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            clip_response = create_clip(
                request.data['text_input'],
                request.data['presenter_id'],
                request.data['driver_id'],
                request.data['bg_color'],
                request.data['subtitle'],
                request.data['voice_id'],
                request.data['provider_id'],
                request.data['speed_rate'],
            )

            # Check if the operation was successful
            if clip_response.get("success"):
                # Save response data to model
                response_data = clip_response["data"]
                ClipResponse.objects.create(
                    user_prompt=request.data['text_input'],
                    clip_id=response_data["id"],
                    created_at=datetime.fromisoformat(response_data["created_at"]),
                    object_type=response_data["object"],
                    status=response_data["status"]
                )   
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Clip created successfully","data":response_data})

            # Handle error case
            return Response({"error": clip_response.get("error", "Failed to create clip")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)



class CreateTalkView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user_limit,created = UserAIStudioLimit.objects.get_or_create(user=request.user)
        if user_limit.limit > 0:
            image_id = request.data.get('image_id', None)
            if image_id:
                try:
                    image = TalkImages.objects.get(id=image_id)
                    image_url = settings.SITE_DOMAIN + image.big_image.url
                    # logger.info("Image URL from ID: %s", image_url)
                except TalkImages.DoesNotExist:
                    return Response({"error": "Image not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                image = request.FILES.get('image')
                if not image:
                    return Response({"error": "Image file is required."}, status=status.HTTP_400_BAD_REQUEST)
                image_path = default_storage.save('uploads/' + image.name, ContentFile(image.read()))
                image_url = settings.SITE_DOMAIN + settings.MEDIA_URL + image_path
                # logger.info("Image upload URL: %s", image_url)
            # # Temporary image URL for testing
            # image_url = "https://dev.flxdevpanel.com/media/talk-images/big/Rectangle.png"

            # Validate other required fields
            required_fields = ['text_input', 'fluent', 'expression', 'speed_rate', 'voice_id', 'provider_id', 'subtitle']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(
                        {"error": f"'{field}' field is required and cannot be empty."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Call create_talk with validated data and image URL
            talk_response = create_talk(
                request.data['text_input'],
                image_url,
                request.data['fluent'],
                request.data['expression'],
                request.data['speed_rate'],
                request.data['voice_id'],
                request.data['subtitle'],
                request.data['provider_id'],
            )

            # Check if the operation was successful
            if talk_response.get("success"):
                # Save response data to model
                response_data = talk_response["data"]
                TalkResponse.objects.create(
                    user_prompt=request.data['text_input'],
                    image_link=image_url,
                    talk_id=response_data["id"],
                    created_at=datetime.fromisoformat(response_data["created_at"]),
                    created_by=response_data["created_by"],
                    status=response_data["status"]
                )
                user_limit.limit -= 1
                user_limit.save()
                return Response({"message": f"Talk created successfully","data":response_data})

            # Handle error case
            return Response({"error": talk_response.get("error", "Failed to create talk")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error":"You are out of Energy"},
                        status=status.HTTP_400_BAD_REQUEST)


class CategoriesListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CategoriesModel.objects.all()
    serializer_class = OpenAICategoriesSerializer
    # pagination_class = CustomPagination
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)  # Get the original response
        response_data = {
            'categories': response.data
        }
        return Response(response_data)

class OpenAICategoryListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OpenAIChatCategoriesSerializer
    # pagination_class = CustomPagination

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given category,
        by filtering against a `category_id` query parameter in the URL.
        """
        queryset = OpenAIChatCategories.objects.all()
        category_id = self.request.query_params.get('category_id')
        if category_id is not None:
            queryset = queryset.filter(category=category_id)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)  # Get the original response
        response_data = {
            'chat_categories': response.data
        }
        return Response(response_data)


class DeleteUserHistory(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def delete_history(self, request):
        user = request.user
        try:
            OpenAIChatInteraction.objects.filter(user=user).delete()
            OpenAIAudioInteraction.objects.filter(user=user).delete()
            OpenAIImageInteraction.objects.filter(user=user).delete()

            return Response({"success": True, "message": "User history deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": "Something happened while trying to delete your history: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OpenAIChatInteractionView(CreateAPIView):
    queryset = OpenAIChatInteraction.objects.all()
    serializer_class = OpenAIChatInteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_prompt = self.request.data.get('user_text_prompt')
        response_type = self.request.data.get('response_type', 'detailed')  # default to 'detailed' if not specified
        chat_id = self.request.data.get('chat_id')  # Get chat_id from the request
        if chat_id:
            try:
                chat_instance = OpenAIChatID.objects.get(chat_id=chat_id)
            except OpenAIChatID.DoesNotExist:
                pass
                # If chat_id does not exist, raise a ValidationError
        #         raise ValidationError({'chat_id': ['Chat ID does not exist.']})
        # else:
        #     # If no chat_id is provided, raise a ValidationError
        #     raise ValidationError({'chat_id': ['Chat ID is required.']})
        

        user_chat_history = OpenAIChatInteraction.objects.filter(user=self.request.user)
        chat_history_messages = [
            {"role": "assistant", "content": chat.gpt_response} for chat in user_chat_history
        ]
        # if response_type != "detailed":
        #     assistant_type = OpenAIChatCategories.objects.get(id=response_type)
        #     messages = [
        #         {"role": "system", "content": f"You are a helpful assistant. Please provide a {assistant_type.admin_description} response."},
        #         *chat_history_messages,
        #         {"role": "user", "content": user_prompt}
        #     ]
        # else:
        messages = [
            {"role": "system", "content": f"You are a helpful assistant."},
            *chat_history_messages,
            {"role": "user", "content": user_prompt}
        ]
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages
        )
        
        gpt_response = completion.choices[0].message.content
        try:
            serializer.save(user=self.request.user, user_text_prompt=user_prompt,gpt_response=gpt_response, chat=chat_instance)
        except:
            serializer.save(user=self.request.user, gpt_response=gpt_response, user_text_prompt=user_prompt)

# class OpenAIChatInteractionView(CreateAPIView):
#     queryset = OpenAIChatInteraction.objects.all()
#     serializer_class = OpenAIChatInteractionSerializer
#     permission_classes = [IsAuthenticated]

#     def perform_create(self, serializer):
#         user_prompt = self.request.data.get('user_text_prompt')
#         user_chat_history = OpenAIChatInteraction.objects.filter(user=self.request.user)
#         # if user_chat_history:
#         chat_history_messages = [
#             {"role": "assistant", "content": chat.gpt_response} for chat in user_chat_history
#             # {"role": "assistant", "content": 'Flibbo is an AI powered social media'} 
#         ]
#         # else:
#         #     chat_history_messages = [
#         #         {"role": "assistant", "content": 'Flibbo is An AI powered Social Media'}
#         #     ]
#         messages = [
#             {"role": "system", "content": "You are a helpful assistant."},
#             *chat_history_messages,
#             {"role": "user", "content": user_prompt}
#         ]
#         completion = client.chat.completions.create(
#             model="gpt-4-1106-preview",
#             messages=messages
#         )
        
#         # Extract GPT response message
#         gpt_response = completion.choices[0].message.content  # Corrected line

#         # Save model instance
#         serializer.save(user=self.request.user, gpt_response=gpt_response)


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

        chat_id = self.request.data.get('chat_id')  # Get chat_id from the request
        if chat_id:
            try:
                chat_instance = OpenAIChatID.objects.get(chat_id=chat_id)
            except OpenAIChatID.DoesNotExist:
                pass
                # If chat_id does not exist, raise a ValidationError
        #         raise ValidationError({'chat_id': ['Chat ID does not exist.']})
        # else:
        #     # If no chat_id is provided, raise a ValidationError
        #     raise ValidationError({'chat_id': ['Chat ID is required.']})

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
            try:
                serializer.save(user=self.request.user, gpt_response=gpt_response, user_audio_prompt=audio_file, chat=chat_instance)
            except:
                serializer.save(user=self.request.user, gpt_response=gpt_response, user_audio_prompt=audio_file)

        finally:
            os.remove(temp_file_path)



    def is_supported_format(self, file_name):
        supported_formats = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']
        return any(file_name.endswith('.' + fmt) for fmt in supported_formats)

 



class OpenAITextToSpeechInteractionView(CreateAPIView):
    queryset = OpenAITextToSpeechInteraction.objects.all()
    serializer_class = OpenAITextToSpeechInteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_prompt = self.request.data.get('user_text_prompt')
        chat_id = self.request.data.get('chat_id')  # Get chat_id from the request
        if chat_id:
            try:
                chat_instance = OpenAIChatID.objects.get(chat_id=chat_id)
            except OpenAIChatID.DoesNotExist:
                pass
                # If chat_id does not exist, raise a ValidationError
        #         raise ValidationError({'chat_id': ['Chat ID does not exist.']})
        # else:
        #     # If no chat_id is provided, raise a ValidationError
        #     raise ValidationError({'chat_id': ['Chat ID is required.']})

        try:
            # Convert the user prompt to speech
            response = openai.Audio.speech.create(
                model="tts-1",
                voice="nova",
                input=user_prompt,
            )

            # Save the audio response
            with open("output.mp3", "wb") as audio_file:
                audio_file.write(response)

            # Save the model instance with the user prompt
            try:
                serializer.save(user=self.request.user, gpt_response=gpt_response, chat=chat_instance)
            except:
                serializer.save(user=self.request.user, gpt_response=gpt_response)
                
        except Exception as e:
            # Handle exceptions (logging, custom error messages, etc.)
            print(f"An error occurred: {e}")



# image_url = response.data[0].url

class OpenAIImageInteractionView(CreateAPIView):
    queryset = OpenAIImageInteraction.objects.all()
    serializer_class = OpenAIImageInteractionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        image_text = self.request.data.get('user_text_prompt_image')
        n_cout_str = self.request.data.get('n_cout', '1')  # default to 1 if not provided
        chat_id = self.request.data.get('chat_id')  # Get chat_id from the request
        if chat_id:
            try:
                chat_instance = OpenAIChatID.objects.get(chat_id=chat_id)
            except OpenAIChatID.DoesNotExist:
                pass
                # If chat_id does not exist, raise a ValidationError
        #         raise ValidationError({'chat_id': ['Chat ID does not exist.']})
        # else:
        #     # If no chat_id is provided, raise a ValidationError
        #     raise ValidationError({'chat_id': ['Chat ID is required.']})

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
        try:
            save_dict = {'user': self.request.user,'chat':chat_instance, 'user_text_prompt_image':image_text}
        except:
            save_dict = {'user': self.request.user, 'user_text_prompt_image':image_text}

        for i in range(1):
            # Access each image URL in the response
            image_url = response.data[i].url
            save_dict[f'gpt_response{i + 1}'] = image_url

        serializer.save(**save_dict)




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

class OpenAIChatInteractionViewe(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_prompt = request.data.get('user_text_prompt')
        history = request.data.get('user_text_history')
        key = request.data.get('key')
        if key == "TheKey!1@":
            if history:
                chat_history_messages = [
                    {"role": "assistant", "content": history}
                ]

                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    *chat_history_messages,
                    {"role": "user", "content": user_prompt}
                ]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt}
                ]


            completion = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )

            # Extract GPT response message
            gpt_response = completion.choices[0].message.content

            return Response({"gpt_response": gpt_response})
        return Response({"gpt_response": 'Your Are not Allowed'})



class OpenAIChatInteractionViewe3(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extracting parameters from the request body
        user_prompt = request.data.get('user_text_prompt')
        key = request.data.get('key')
        name = request.data.get('name')
        last_name = request.data.get('last_name')
        customer_status = request.data.get('customer_status')
        description = request.data.get('description')

        # Key validation
        if key == "TheKey!1@":
            # Preparing chat history messages

            # Including the additional parameters in the messages
            # You can modify this part according to how you want to use these parameters
            if description:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""به عنوان مثال ،  {name} {last_name} که وضعیت ارتباط من با او  {customer_status} است  و {description} چیکار کنم که به مشتری مشتاق  و درجه یک من تبدیل شود ؟
                        در 3 خط به من توضیح بده و اسم و فامیلی که بهت گفتم رو داخل متن حتما قرار بده. 
                        """}
                ]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""به عنوان مثال ،  {name} {last_name} که وضعیت ارتباط من با او  {customer_status} است  و مشتری جدید من است که میخواهم به او خدماتم را ارائه کنم. چیکار کنم که به مشتری مشتاق  و درجه یک من تبدیل شود ؟
                    در 3 خط به من توضیح بده. و اسم و فامیلی که بهت گفتم رو داخل متن حتما قرار بده """}
                                    ]
            # Generating the completion
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )

            # Extract GPT response message
            gpt_response = completion.choices[0].message.content

            return Response({"description": gpt_response})
        return Response({"description": 'You Are not Allowed'})