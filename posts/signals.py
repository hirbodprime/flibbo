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
from .consumers import HomeConsumer
# Reuse the same logger
logger = logging.getLogger('tweet_app')

# @receiver(post_save, sender=TweetPostModel)
# def broadcast_new_post(sender, instance, created, **kwargs):
#     if created:
#         # Prepare a simple message or notification
#         message = {
#             'type': 'new_post',
#             'message': 'A new post has been created!',
#             # You can include minimal information like post ID if needed
#             'post_id': instance.id
#         }
        
#         # Use channel layer to broadcast the message
#         channel_layer = get_channel_layer()
#         # Ensure the async function is called in a synchronous context
#         async_to_sync(channel_layer.group_send)(
#             'home',  # The group name where clients are listening
#             message
#         )
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
            compress_image(instance.image.path)
            logger.debug(f"Compressed image for TweetPostImagesModel id: {instance.id}")

        if instance.video:
            compress_video(instance.video.path)
            logger.debug(f"Compressed video for TweetPostImagesModel id: {instance.id}")
    except Exception as e:
        logger.error(f"Error compressing media for TweetPostImagesModel id: {instance.id}: {e}")

def compress_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.save(image_path, optimize=True, quality=50)
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

# @receiver(post_save, sender=TweetPostImagesModel)
# def compress_media(sender, instance, **kwargs):
#     if instance.image:  # Compress image if present
#         compress_image(instance.image.path)

#     if instance.video:  # Compress video if present
#         compress_video(instance.video.path)

# def compress_image(image_path):
#     with Image.open(image_path) as img:
#         # Adjust the quality of the image here (1-100)
#         img.save(image_path, optimize=True, quality=50)

# def compress_video(video_path):
#     clip = VideoFileClip(video_path)
#     # You can adjust the target bitrate as needed for compression
#     target_bitrate = "500k"
#     temp_video_path = video_path + "_temp.mp4"
#     clip.write_videofile(temp_video_path, bitrate=target_bitrate)
#     os.replace(temp_video_path, video_path)  # Replace original with compressed


