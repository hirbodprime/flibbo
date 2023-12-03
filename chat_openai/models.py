# my_app/models.py
from django.contrib.auth import get_user_model
from django.db import models
User = get_user_model()

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

