# my_app/models.py
from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()

expression_choice = (
    ('happy','happy'),
    ('neutral','neutral'),
    ('serious','serious'),
    ('suprise','suprise'),
    )
# voice_id, aspectratio, bg_music
class FlikiVideoModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    image_link = models.TextField(null=True,blank=True) 
    text_input = models.TextField(null=True,blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    voice_id = models.TextField()
    aspectratio = models.CharField(max_length=100)
    video_id = models.TextField(null=True,blank=True)
    bg_music = models.CharField(max_length=100)


class VoiceActorModel(models.Model):
    country = models.CharField(max_length=100, blank=True, null=True)
    voice_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    locale = models.CharField(max_length=50)
    language = models.CharField(max_length=100)
    access = models.CharField(max_length=50)
    provider = models.CharField(max_length=50)
    styles = models.JSONField(default=list)

    def __str__(self):
        return self.name

class UserAIStudioLimit(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    limit = models.IntegerField(default=20)
    def __str__(self):
        return f"{self.user} - {self.limit}"


class StyleListModel(models.Model):
    name = models.CharField(max_length=256,null=True,blank=True)
    image = models.FileField(upload_to='ai/styles/',null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class TextToImageResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    style = models.ForeignKey(StyleListModel, on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image_link = models.TextField(null=True,blank=True) 
    text_input = models.TextField(null=True,blank=True) 

    def __str__(self):
        return f'{self.style} - {self.user}'


class TextToSpeechResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    audio_link = models.TextField(null=True,blank=True) 
    text_input = models.TextField(null=True,blank=True) 
    voice_id = models.TextField(null=True,blank=True) 

    def __str__(self):
        return f'{self.style} - {self.user}'


class AIToolsModel(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    bg_image = models.FileField(upload_to='ai/',null=True,blank=True)
    icon_image = models.FileField(upload_to='ai/',null=True,blank=True)
    short_description = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name




class TalkResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    talk_id = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.talk_id

class ClipResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    clip_id = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    object_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.clip_id   

class AnimationResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    animation_id = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    object_type = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.animation_id   


class CategoriesModel(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name



class OpenAIChatCategories(models.Model):
    category = models.ForeignKey(CategoriesModel, on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    hex_code = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.FileField(upload_to='icons/',null=True,blank=True)
    def __str__(self):
        return self.name

class OpenAIChatChatID(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    chat_id = models.IntegerField()

    def __str__(self):
        return self.user_text_prompt[:50]


class OpenAIChatInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    user_text_prompt = models.TextField()
    gpt_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_text_prompt[:50]


class OpenAIAudioInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    user_audio_prompt = models.FileField()
    gpt_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gpt_response[:50]


class OpenAIImageInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    user_text_prompt_image = models.TextField(max_length=1000)
    n_cout = models.IntegerField(default=1)
    gpt_response1 = models.TextField(max_length=1000,null=True,blank=True)
    gpt_response2 = models.TextField(max_length=1000,null=True,blank=True)
    gpt_response3 = models.TextField(max_length=1000,null=True,blank=True)
    gpt_response4 = models.TextField(max_length=1000,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gpt_response1[:50]


class OpenAITextToSpeechInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    user_text_prompt = models.TextField()
    gpt_response = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gpt_response[:50]

