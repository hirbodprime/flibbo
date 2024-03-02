from django.db.models.signals import post_save,pre_save,m2m_changed
from django.dispatch import receiver
from .models import ReportPost, TweetPostModel, TweetCommentModel, TweetPostImagesModel
from posts.api.serializers import TweetPostSerializer
from PIL import Image
from moviepy.editor import VideoFileClip
import os
import logging
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .api.serializers import TweetCommentWebSocketSerializer
from .consumers import HomeConsumer
# Reuse the same logger
logger = logging.getLogger('tweet_app')

# Mock request context generator
def get_mock_request(user):
    return {
        'request': type('Request', (object,), {'user': user, 'META': {}})()
    }

@receiver(post_save, sender=TweetCommentModel)
def new_comment_signal(sender, instance, created, **kwargs):
    print(f"New comment signal triggered for post {instance.post.id}")
    if created:
        channel_layer = get_channel_layer()
        group_name = f'home'

        # Instead of a full request, manually create a context with the necessary data
        context = get_mock_request(instance.user)
        
        # Serialize the new comment using the mock request context
        comment_data = TweetCommentWebSocketSerializer(instance, context=context).data

        # Use async_to_sync to call the asynchronous group_send method
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'new_comment_notification',
                'message': {
                    'comment': comment_data,
                    'post_id': instance.post.id,
                    'total_comments': TweetCommentModel.objects.filter(post=instance.post).count()
                }
            }
        )


@receiver(post_save, sender=TweetPostModel)
def broadcast_new_post(sender, instance, created, **kwargs):
    if created:
        # Just signal that a new post has been created
        asyncio.run(HomeConsumer.broadcast_new_post_notification())
@receiver(post_save, sender=TweetPostModel)
def create_share_link(sender, created, instance, **kwargs):
    if created:
        from firebase_dynamic_links import dynamic_link_builder
        builder = dynamic_link_builder(api_key='AIzaSyBq77V9pbQXFDoM-eOK5G67NB6GxvXXBcc')
        options = {
            'link': f'https://flibbo.com/share?post={instance.id}',
            'apn': 'com.flibbo.app', 
            'ibi': 'com.flibbo.app'
        }
        try:
            short_link = builder.generate_short_link(app_code='flibbo', **options)
            instance.share_post = short_link
            instance.save()
        except Exception as e:
            print(str(e))
@receiver(m2m_changed, sender=TweetCommentModel.reported_by.through)
def delete_comment_on_100_reports(sender, instance, **kwargs):
    if instance.reported_by.count() >= 100:
        instance.delete()

@receiver(post_save, sender='posts.ReportPost')  # Replace 'your_app_name' with the name of your Django app
def delete_post_if_reports_exceed_threshold(sender, instance, **kwargs):
    if instance.report_count >= 200:
        post_to_delete = TweetPostModel.objects.get(id=instance.post.id)  # Keep a reference to the post instance\
        post_to_delete.hide = True
        post_to_delete.save()


@receiver(post_save, sender=TweetPostImagesModel)
def compress_media(sender, instance, **kwargs):
    try:
        if instance.image:
            compress_image(instance.image.path,50)
            logger.debug(f"Compressed image for TweetPostImagesModel id: {instance.id}, field: image")

        if instance.video:
            compress_video(instance.video.path,50)
            logger.debug(f"Compressed video for TweetPostImagesModel id: {instance.id}, field: video")

        # Check and compress cover_image if exists
        if instance.cover_image:
            compress_image(instance.cover_image.path,10)
            logger.debug(f"Compressed cover image for TweetPostImagesModel id: {instance.id}, field: cover_image")

        # Check and compress cover_video if exists
        if instance.cover_video:
            compress_video(instance.cover_video.path,10)
            logger.debug(f"Compressed cover video for TweetPostImagesModel id: {instance.id}, field: cover_video")

    except Exception as e:
        logger.error(f"Error compressing media for TweetPostImagesModel id: {instance.id}: {e}")

def compress_image(image_path,quality):

    try:
        with Image.open(image_path) as img:
            img.save(image_path, optimize=True, quality=quality)
            logger.debug(f"Image compressed: {image_path}")
    except Exception as e:
        logger.error(f"Error compressing image: {image_path}: {e}")

def compress_video(video_path):
    try:
        clip = VideoFileClip(video_path)
        target_bitrate = "500k"
        temp_video_path = video_path + "_temp.mp4"
        clip.write_videofile(temp_video_path, bitrate=target_bitrate)
        os.replace(temp_video_path, video_path)
        logger.debug(f"Video compressed: {video_path}")
    except Exception as e:
        logger.error(f"Error compressing video: {video_path}: {e}")



