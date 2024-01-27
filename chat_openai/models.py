# my_app/models.py
from django.contrib.auth import get_user_model
from django.db import models
from .extract_cover_images import extract_and_save_cover

User = get_user_model()

expression_choice = (
    ('happy','happy'),
    ('neutral','neutral'),
    ('serious','serious'),
    ('suprise','suprise'),
    )
# voice_id, aspectratio, bg_music
class SuggestPromptsModel(models.Model):
    prompt = models.TextField()
    def __str__(self):
        return self.prompt
class SuggestPromptsImageModel(models.Model):
    prompt = models.TextField()
    def __str__(self):
        return self.prompt

class Dialect(models.Model):
    _id = models.CharField(max_length=50, unique=True,null=True,blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    name_post_space = models.CharField(max_length=100, null=True, blank=True)
    initials = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return f'{self.name_post_space}'

class Language(models.Model):
    _id = models.CharField(max_length=50, unique=True,null=True,blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.name
class LanguageAndDialectRelation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    dialect = models.ForeignKey(Dialect, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.language} {self.dialect}'
        
class ToolsOptionsModel(models.Model):
    CHOICES = (
        ('talk', 'Talk'),
        ('clip', 'Clip'),
        ('fliki-video', 'Fliki-Video'),
        # ... add other choices here ...
    )

    choice_field = models.CharField(max_length=15, choices=CHOICES)
    
    # talk fields
    fluent = models.BooleanField(default=True)
    subtitle = models.BooleanField(default=True)
    expression = models.BooleanField(default=True)
    speed_rate = models.BooleanField(default=True)
    
    # clip fields
    bg_color = models.BooleanField(default=True)
    
    # animation fields
    # text to image fields
    # text to speech fields

    # fliki video fields
    aspectratio = models.BooleanField(default=True)
    bg_music = models.BooleanField(default=True)
    def __str__(self):
        return self.choice_field
    

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
        return f"{self.name} - {self.locale} - {self.voice_id}- {self.language}"

class UserAIStudioLimit(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    limit = models.IntegerField(default=20)
    def __str__(self):
        return f"{self.user} - {self.limit}"


class StyleListModel(models.Model):
    name = models.CharField(max_length=256,null=True,blank=True)
    name2 = models.CharField(max_length=256,null=True,blank=True)
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
    duration = models.TextField(null=True,blank=True) 

    def __str__(self):
        return f'{self.user} - {self.duration}'

enum_choices = (
        ('Talk', 'Talk'),
        ('Clip', 'Clip'),
        ('Image-Animator', 'Image-Animator'),
        ('Text-to-Image', 'Text-to-Image'),
        ('Text-to-Speech', 'Text-to-Speech'),
        ('Create-Video', 'Create-Video'),
    )

class AIToolsModel(models.Model):
    options = models.ForeignKey(ToolsOptionsModel, on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    tools_type = models.CharField(max_length=255,choices=enum_choices,null=True,blank=True)
    bg_image = models.FileField(upload_to='ai/',null=True,blank=True)
    icon_image = models.FileField(upload_to='ai/',null=True,blank=True)
    short_description = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name




class TalkImages(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.FileField(upload_to='talk-images/',null=True,blank=True,max_length=400)
    big_image = models.FileField(upload_to='talk-images/big/',null=True,blank=True,max_length=1400)
    def __str__(self):
        return f'{self.id}'

class TalkResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    user_prompt = models.TextField(null=True,blank=True)
    image_link = models.TextField(null=True,blank=True)
    talk_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.talk_id



class ClipResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    clip_id = models.CharField(max_length=100)
    user_prompt = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.clip_id   

class AnimationResponse(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    animation_id = models.CharField(max_length=100)
    animation_name = models.TextField(null=True,blank=True)
    animation_number = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.animation_id   
    def save(self, *args, **kwargs):
        # Check if the instance is new
        if not self.pk:
            last = AnimationResponse.objects.all().order_by('animation_number').last()
            if last:
                # Increment the animation number from the last instance
                self.animation_number = last.animation_number + 1

        # Update animation_name with the new animation_number
        self.animation_name = f"animation_export_{self.animation_number}"

        super(AnimationResponse, self).save(*args, **kwargs)

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
    admin_description = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.FileField(upload_to='icons/',null=True,blank=True)
    def __str__(self):
        return self.name



class OpenAIChatID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    chat_id = models.TextField(unique=True)  # Ensure chat_id is unique

    def __str__(self):
        return f"Chat {self.chat_id} ({self.user.username})"  # Adjusted for better representation

class OpenAIChatInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(OpenAIChatID, on_delete=models.CASCADE,null=True, blank=True)  # Link to OpenAIChatID
    user_text_prompt = models.TextField()
    gpt_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_text_prompt[:50]



class OpenAIAudioInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    user_audio_prompt = models.FileField()
    chat = models.ForeignKey(OpenAIChatID, on_delete=models.CASCADE,null=True, blank=True)  # Link to OpenAIChatID
    gpt_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gpt_response[:50]


class OpenAIImageInteraction(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    chat = models.ForeignKey(OpenAIChatID, on_delete=models.CASCADE,null=True, blank=True)  # Link to OpenAIChatID
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
    chat = models.ForeignKey(OpenAIChatID, on_delete=models.CASCADE,null=True, blank=True)  # Link to OpenAIChatID
    gpt_response = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gpt_response[:50]


photo_style = (
    ('normal','normal'),
    ('circle','circle')
    )

class HeyGenCreateVideoModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    background = models.CharField(max_length=255)
    ratio = models.CharField(max_length=255)
    avatar_id = models.CharField(max_length=255,null=True,blank=True)
    talking_photo_id = models.CharField(max_length=255,null=True,blank=True)
    avatar_style = models.CharField(max_length=255,null=True,blank=True)
    caption = models.TextField(null=True,blank=True)
    input_text = models.TextField(null=True,blank=True)
    video_id = models.TextField()
    voice_id = models.CharField(max_length=255)
    input_audio = models.FileField(upload_to="heygen/audios/", null=True,blank=True)
    talking_photo_style = models.CharField(max_length=255,choices=photo_style,null=True,blank=True)

class HeyGenCreateVideoTranslateModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    video_id = models.TextField()
    voice_id = models.CharField(max_length=255)

class HeyGenTalkingPhotoIDModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    image_url = models.TextField()
    image_id = models.TextField()
