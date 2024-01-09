# my_app/serializers.py

from rest_framework import serializers
from chat_openai.models import SuggestPromptsImageModel,SuggestPromptsModel,OpenAIChatID,TalkImages,ToolsOptionsModel,VoiceActorModel,StyleListModel,OpenAIChatInteraction,AIToolsModel,CategoriesModel,OpenAIAudioInteraction,OpenAIImageInteraction,OpenAIChatCategories
from django.conf import settings


class TalkVoiceActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceActorModel
        fields = '__all__'  

class OpenAIChatIDSerializer(serializers.ModelSerializer):
    first_message = serializers.CharField(required=True)  # Explicitly set as required
    

    class Meta:
        model = OpenAIChatID
        fields = ['user', 'first_message', 'created_at','chat_id']
    read_only_fields = ('chat_id', 'user')  # Making user read-only
    def __init__(self, *args, **kwargs):
        super(OpenAIChatIDSerializer, self).__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['chat_id'].required = False

class TalkImagesListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    def get_image(self,obj):
        if obj.image:
            return f"{settings.SITE_DOMAIN}{obj.image.url}"
        return 
    class Meta:
        model = TalkImages
        fields = ['id','image']

class VoiceActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceActorModel
        fields = ['country', 'voice_id', 'name', 'gender', 'locale', 'language', 'access', 'provider', 'styles']


class StylesModelSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    def get_description(self,obj):
        if obj.description:
            return obj.description
        return 
    def get_image(self,obj):
        if obj.image:
            return f"{settings.SITE_DOMAIN}{obj.image.url}"
        return 
    class Meta:
        model = StyleListModel
        fields = ['id','name', 'image','description', 'created_at']

class ToolsOptionsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolsOptionsModel
        fields = '__all__' 
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Add logic here to filter out fields based on the choice_field
        if instance.choice_field == 'talk':
            # Keep only fields relevant to 'talk'
            ret = {key: value for key, value in ret.items() if key in ['fluent', 'subtitle', 'expression', 'speed_rate']}
        elif instance.choice_field == 'clip':
            # Keep only fields relevant to 'clip'
            ret = {key: value for key, value in ret.items() if key in ['bg_color']}
        # ... Add more conditions for other choices if necessary
        elif instance.choice_field == 'fliki-video':
            # Keep only fields relevant to 'clip'
            ret = {key: value for key, value in ret.items() if key in ['aspectratio','bg_music']}
        return ret

class AIToolsModelSerializer(serializers.ModelSerializer):
    icon_image = serializers.SerializerMethodField()
    bg_image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    options = ToolsOptionsModelSerializer(read_only=True) 
    def get_description(self,obj):
        if obj.description:
            return obj.description
        return 
    def get_icon_image(self,obj):
        if obj.icon_image:
            return f"{settings.SITE_DOMAIN}{obj.icon_image.url}"
        return 
    def get_bg_image(self,obj):
        if obj.bg_image:
            return f"{settings.SITE_DOMAIN}{obj.bg_image.url}"
        return 
    class Meta:
        model = AIToolsModel
        fields = ['tools_type','name', 'options','short_description', 'bg_image','icon_image','description', 'created_at']



class OpenAICategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesModel
        fields = ('id','name','created_at')

class OpenAIChatCategoriesSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    class Meta:
        model = OpenAIChatCategories
        fields = ('id','name','icon','hex_code','description','created_at')
    def get_icon(self,obj):
        if obj.icon:
            return f"{settings.SITE_DOMAIN}{obj.icon.url}"
        else:
            return 


class OpenAIChatInteractionSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    def get_chat(self,obj):
        if obj.chat:
            return obj.chat.chat_id
        else:
            return
    class Meta:
        model = OpenAIChatInteraction
        fields = ('id', 'user', 'chat', 'user_text_prompt', 'gpt_response', 'created_at')
        read_only_fields = ('user', 'chat', 'created_at', 'gpt_response')

class OpenAIAudioInteractionSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    def get_chat(self,obj):
        if obj.chat:
            return obj.chat.chat_id
        else:
            return
    class Meta:
        model = OpenAIAudioInteraction
        fields = ('id', 'user', 'chat', 'user_audio_prompt','gpt_response', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response')


class OpenAIImageInteractionSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    def get_chat(self, obj):
        try:
            return obj.chat.chat_id if obj.chat else None
        except AttributeError:
            # Handle cases where 'obj' does not have a 'chat' attribute
            return None

    class Meta:
        model = OpenAIImageInteraction
        fields = ('id', 'user', 'chat', 'user_text_prompt_image','gpt_response1','gpt_response2','gpt_response3','gpt_response4','n_cout', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response1','gpt_response2','gpt_response3','gpt_response4')
    
    

class ChatInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenAIChatInteraction
        fields = '__all__'

class AudioInteractionSerializer(serializers.ModelSerializer):
    user_audio_prompt = serializers.SerializerMethodField()
    chat = serializers.SerializerMethodField()
    def get_chat(self,obj):
        if obj.chat:
            return obj.chat.chat_id
        else:
            return
    class Meta:
        model = OpenAIAudioInteraction
        fields = '__all__'
    def get_user_audio_prompt(self, obj):
        return f"{settings.SITE_DOMAIN}/media/{obj.user_audio_prompt}"

class ImageInteractionSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    def get_chat(self,obj):
        if obj.chat:
            return obj.chat.chat_id
        else:
            return
    class Meta:
        model = OpenAIImageInteraction
        fields = '__all__'
    




class OpenAITextToSpeechInteractionSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField()
    def get_chat(self,obj):
        if obj.chat:
            return obj.chat.chat_id
        else:
            return
    class Meta:
        model = OpenAIAudioInteraction
        fields = ('id', 'user', 'chat', 'user_text_prompt','gpt_response', 'created_at')
        read_only_fields = ('user', 'created_at', 'gpt_response')

class SuggestPromptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestPromptsModel
        fields = ['prompt']


class SuggestPromptsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestPromptsImageModel
        fields = ['prompt']