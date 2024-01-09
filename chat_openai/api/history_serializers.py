from rest_framework import serializers
from chat_openai.models import TalkResponse, ClipResponse, AnimationResponse, TextToImageResponse, TextToSpeechResponse, FlikiVideoModel

class TalkResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalkResponse
        fields = ['user_prompt','talk_id']

class ClipResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClipResponse
        fields = ['user_prompt','clip_id']

class AnimationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimationResponse
        fields = ['animation_name','animation_id']  # Assuming this is the field you need

class TextToImageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToImageResponse
        fields = ['text_input','image_link']

class TextToSpeechResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToSpeechResponse
        fields = ['text_input','audio_link']

class FlikiVideoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlikiVideoModel
        fields = ['text_input','video_id']











# return based on model type
# class UserPromptView(APIView):
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         model_type = request.query_params.get('model_type')

#         if model_type == 'talk':
#             instance = get_object_or_404(TalkResponse, user=user)
#             serializer = TalkResponseSerializer(instance)
#         elif model_type == 'clip':
#             instance = get_object_or_404(ClipResponse, user=user)
#             serializer = ClipResponseSerializer(instance)
#         elif model_type == 'animation':
#             instance = get_object_or_404(AnimationResponse, user=user)
#             serializer = AnimationResponseSerializer(instance)
#         elif model_type == 'text_to_image':
#             instance = get_object_or_404(TextToImageResponse, user=user)
#             serializer = TextToImageResponseSerializer(instance)
#         elif model_type == 'text_to_speech':
#             instance = get_object_or_404(TextToSpeechResponse, user=user)
#             serializer = TextToSpeechResponseSerializer(instance)
#         elif model_type == 'fliki_video':
#             instance = get_object_or_404(FlikiVideoModel, user=user)
#             serializer = FlikiVideoModelSerializer(instance)
#         else:
#             return Response({'error': 'Invalid model type'}, status=status.HTTP_400_BAD_REQUEST)
