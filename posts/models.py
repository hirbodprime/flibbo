from django.db import models
from django.urls import reverse
import os
from category.models import CategoryModel, SubCategoryModel
from moviepy.editor import VideoFileClip
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from posts.utils.upload_image import PostUploadHandler 

from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_countries.fields import CountryField
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
User = get_user_model()

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_photo_sizes(request, tweet_post_id):
    # Retrieve the TweetPostModel instance by ID
    tweet_post = get_object_or_404(TweetPostModel, pk=tweet_post_id)

    # Calculate sizes in megabytes
    photo_size_mb = tweet_post.photo.size / (1024 * 1024) if tweet_post.photo else 0
    # photo_compressed_size_mb = tweet_post.photo_compressed.size / (1024 * 1024) if tweet_post.photo_compressed else 0

    # Prepare the response data
    data = {
        'photo_size_mb': round(photo_size_mb, 2),
        # 'photo_compressed_size_mb': round(photo_compressed_size_mb, 2)
    }

    return JsonResponse(data)

upload_image_post_handler = PostUploadHandler('post_images', 'image', 'images')
upload_video_post_handler = PostUploadHandler('post_videos', 'video', 'videos')
upload_book_post_handler = PostUploadHandler('post_book', 'book', 'books')
upload_podcast_post_handler = PostUploadHandler('post_podcast', 'podcast', 'podcasts')

def upload_podcast_post(instance, filename):
    return upload_podcast_post_handler.get_filename(instance, filename)

def upload_book_post(instance, filename):
    return upload_book_post_handler.get_filename(instance, filename)

def upload_image_post(instance, filename):
    new_filename = filename[:100]
    return upload_image_post_handler.get_filename(instance, new_filename)

def upload_video_post(instance, filename):
    return upload_video_post_handler.get_filename(instance, filename)




class BasePostModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=200, allow_unicode=True, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    hashtag = ArrayField(models.CharField(max_length=100), blank=True, null=True,default=list)
    # location = CountryField(blank=True, null=True,max_length=100)  
    location = models.TextField(blank=True, null=True)
    total_comments = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, blank=True, null=True)
    sub_category = models.ForeignKey(SubCategoryModel, on_delete=models.CASCADE, blank=True, null=True)
    likes = models.ManyToManyField(User, blank=True)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    total_saves = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    viewed_by_users = models.ManyToManyField(User, blank=True,related_name='users_viewed')
    saved_by_users = models.ManyToManyField(User, blank=True)
    shared_by_users = models.ManyToManyField(User, blank=True)
    hide = models.BooleanField(default=False)
    urls = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    photo_blur_hash = models.CharField(max_length=1000, blank=True, null=True)
    height = models.CharField(blank=True, null=True)
    cover = models.ImageField(upload_to=upload_image_post, blank=True, null=True,max_length=2000)
    class Meta:
        # verbose_name_plural = "Posts"
        abstract = True

    def __str__(self):
        return f'{self.id}'

    def save(self, *args, **kwargs):
        import random
        import string
        slug_length = 10  # You can adjust the length of the slug as needed
        random_slug = ''.join(random.choices(string.ascii_letters + string.digits, k=slug_length))
        self.slug = slugify(random_slug)
        if self.cover:
            # Open the uploaded cover image
            pil_image = Image.open(self.cover)

            # Convert RGBA to RGB if needed
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')

            # Resize/compress the image
            output_io_stream = io.BytesIO()
            pil_image.save(output_io_stream, format='JPEG', quality=70)
            output_io_stream.seek(0)

            # Change the cover field value
            self.cover = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                              "%s.jpg" % self.cover.name.split('.')[0], 
                                              'image/jpeg', 
                                              output_io_stream.getbuffer().nbytes, 
                                              None)

        super().save(*args, **kwargs)


    def increment_total_views(self):
        self.total_views += 1
        self.save()
        
    def increment_view_users(self,user):
        self.viewed_by_users.add(user)

    def save_post(self, user):
        self.saved_by_users.add(user)

    def unsave_post(self, user):
        self.saved_by_users.remove(user)

    def share_post(self, user):
        self.shared_by_users.add(user)

    def increment_total_shares(self):
        self.total_shares += 1
        self.save()
        
    def increment_total_comments(self):
        self.total_comments += 1
        self.save()

    def decrement_total_comments(self):
        self.total_comments -= 1
        self.save()
    
    # def total_likes(self):
    #     return self.likes.count()

    # def total_saves(self):
    #     return self.saved_by_users.count()
    
    def increment_total_likes(self):
        self.total_likes += 1
        self.save()
        
    def increment_like_users(self,user):
        self.likes.add(user)


    def dicrement_total_likes(self):
        self.total_likes -= 1
        self.save()
        
    def dicrement_like_users(self,user):
        self.likes.remove(user)


    def increment_total_saves(self):
        self.total_saves += 1
        self.save()
        
    def increment_save_users(self,user):
        self.saved_by_users.add(user)

    def dicrement_total_saves(self):
        self.total_saves -= 1
        self.save()
        
    def dicrement_save_users(self,user):
        self.saved_by_users.remove(user)

class TweetPostModel(BasePostModel):
    video = models.FileField(upload_to=upload_video_post, blank=True, null=True,max_length=2000)
    photo = models.ImageField(upload_to=upload_image_post, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='tweet_posts_liked', blank=True)
    viewed_by_users = models.ManyToManyField(User, related_name='viewed_posts_post', blank=True)
    saved_by_users = models.ManyToManyField(User, related_name='tweet_posts_saved', blank=True)
    shared_by_users = models.ManyToManyField(User, related_name='tweet_posts_shared', blank=True)
    mention_users = models.ManyToManyField(User, blank=True,related_name='tweet_user_mentioned')
    share_post = models.CharField(max_length=600,blank=True, null=True)

    liked_by_user = models.BooleanField(default=False)
    def get_absolute_url(self,post_id):
        from firebase_dynamic_links import dynamic_link_builder
        builder = dynamic_link_builder(api_key='AIzaSyBq77V9pbQXFDoM-eOK5G67NB6GxvXXBcc')
        options = {
            'link': f'https://flibbo.com/share?post={post_id}',
            'apn': 'com.flibbo.app', 
            'ibi': 'com.flibbo.app'
        }
        short_link = builder.generate_short_link(app_code='flibbo', **options)
        return short_link
    def compress_video(self, video_path):
        clip = VideoFileClip(video_path)

        # Maintain the original size
        original_size = clip.size

        # Specify a lower bitrate (e.g., '500k' - can be adjusted as needed)
        # Bitrate effectively controls the quality and size of the video
        bitrate = '500k'  # Example bitrate

        # Create a temporary file path
        temp_path = f"temp_{os.path.basename(video_path)}"

        # Write the video file with the specified bitrate
        clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", bitrate=bitrate)

        return temp_path



    def save(self, *args, **kwargs):
        if self.photo:  # Check if an image has been uploaded
            # Open the uploaded image
            pil_image = Image.open(self.photo)

            # Convert RGBA to RGB if needed
            if pil_image.mode == 'RGBA':
                pil_image = pil_image.convert('RGB')

            # Resize/compress the image
            # You can add logic here to resize if the image is above a certain size
            output_io_stream = io.BytesIO()
            pil_image.save(output_io_stream, format='JPEG', quality=70)  # Adjust the quality parameter as needed
            output_io_stream.seek(0)

            # Change the image field value to be the newly modified image value
            self.photo = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                              "%s.jpg" % self.photo.name.split('.')[0], 
                                              'image/jpeg', 
                                              output_io_stream.getbuffer().nbytes, 
                                              None)
        if self.video:  # Check if a video has been uploaded
            # Save the uploaded video file temporarily
            temp_video_path = default_storage.save(f"temp_{self.video.name}", ContentFile(self.video.read()))

            # Get the full path of the temporary video
            full_temp_video_path = default_storage.path(temp_video_path)

            # Compress the video
            compressed_video_path = self.compress_video(full_temp_video_path)

            # Update self.video with the compressed video
            with open(compressed_video_path, 'rb') as f:
                self.video.save(os.path.basename(compressed_video_path), ContentFile(f.read()), save=False)

            # Clean up the temp files
            os.remove(compressed_video_path)
            default_storage.delete(temp_video_path)

        super(TweetPostModel, self).save(*args, **kwargs)
class BookPostModel(BasePostModel):
    book = models.FileField(upload_to=upload_book_post, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='book_posts_liked', blank=True)
    viewed_by_users = models.ManyToManyField(User, related_name='viewed_posts_book', blank=True)
    saved_by_users = models.ManyToManyField(User, related_name='book_posts_saved', blank=True)
    shared_by_users = models.ManyToManyField(User, related_name='book_posts_shared', blank=True)
    mention_users = models.ManyToManyField(User, blank=True,related_name='book_user_mentioned')
    liked_by_user = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

class ReportPost(models.Model):
    post = models.ForeignKey(TweetPostModel, on_delete=models.SET_NULL, null=True)
    reported_by = models.ManyToManyField(User, related_name='post_reported_by', blank=True)
    report_count = models.BigIntegerField(default=0)
    def reports_count(self):
        return self.report_count


class PodcastPostModel(BasePostModel):
    podcast = models.FileField(upload_to=upload_podcast_post, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='podcast_post_liked', blank=True)
    viewed_by_users = models.ManyToManyField(User, related_name='viewed_posts_podcast', blank=True)
    saved_by_users = models.ManyToManyField(User, related_name='podcast_posts_saved', blank=True)
    shared_by_users = models.ManyToManyField(User, related_name='podcast_posts_shared', blank=True)
    mention_users = models.ManyToManyField(User, blank=True,related_name='podcast_user_mentioned')
    liked_by_user = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('podcast_detail', args=[str(self.id)])



class TweetCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(TweetPostModel, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True,related_name='tweet_likes')
    total_likes = models.PositiveIntegerField(default=0)
    reported_by = models.ManyToManyField(User, blank=True, related_name='reported_comments')  # New field

    def __str__(self):
        return f"Comment by {self.user.username} on {self.id}"


    def increment_total_likes(self):
        self.total_likes += 1
        self.save()
        
    def increment_like_users(self,user):
        self.likes.add(user)

    def dicrement_total_likes(self):
        self.total_likes -= 1
        self.save()
        
    def dicrement_like_users(self,user):
        self.likes.remove(user)
        
class TweetReplyCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(TweetCommentModel, on_delete=models.CASCADE, related_name='tweet_replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True,related_name='tweet_reply_likes')
    def __str__(self):
        return f"Reply by {self.user.username} on {self.created_at}"
    def total_likes(self):
        return self.likes.count()




class PodcastCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(PodcastPostModel, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True,related_name='podcast_likes')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.id}"
    def total_likes(self):
        return self.likes.count()

class PodcastReplyCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(PodcastCommentModel, on_delete=models.CASCADE, related_name='podcast_replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True,related_name='podcast_reply_likes')

    def __str__(self):
        return f"Reply by {self.user.username} on {self.created_at}"

    def total_likes(self):
        return self.likes.count()




class BookCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(BookPostModel, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True,related_name='book_likes')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.id}"
    def total_likes(self):
        return self.likes.count()

class BookReplyCommentModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(BookCommentModel, on_delete=models.CASCADE, related_name='book_replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True,related_name='book_reply_likes')

    def __str__(self):
        return f"Reply by {self.user.username} on {self.created_at}"
    def total_likes(self):
        return self.likes.count()