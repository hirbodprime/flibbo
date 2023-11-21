# my_app/serializers.py

from rest_framework import serializers
from chat_openai.models import OpenAIChatInteraction,OpenAIAudioInteraction,OpenAIImageInteraction

class OpenAIChatInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIChatInteraction
        fields = ('id', 'user', 'user_text_prompt','gpt_response', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response')


class OpenAIAudioInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIAudioInteraction
        fields = ('id', 'user', 'user_audio_prompt','gpt_response', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response')


class OpenAIImageInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIImageInteraction
        fields = ('id', 'user', 'user_text_prompt_image','gpt_response1','gpt_response2','gpt_response3','gpt_response4','n_cout', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response1','gpt_response2','gpt_response3','gpt_response4')
    
    

class ChatInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIChatInteraction
        fields = '__all__'

class AudioInteractionSerializer(serializers.ModelSerializer):
    user_audio_prompt = serializers.SerializerMethodField()

    class Meta:
        model = OpenAIAudioInteraction
        fields = '__all__'
    def get_user_audio_prompt(self, obj):
        site_domain = "app.flxdevpanel.com"  # Replace this with your actual website domain
        return f"https://{site_domain}/media/{obj.user_audio_prompt}"

class ImageInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIImageInteraction
        fields = '__all__'