from django.db.models.signals import post_save,pre_save,m2m_changed
from django.dispatch import receiver
from .models import ReportPost, TweetPostModel, TweetCommentModel
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




from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TweetPostImagesModel
from PIL import Image
from moviepy.editor import VideoFileClip
import os
from django.utils.timezone import now

# Path to the log file (assuming it's in the same directory as views.py)
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'compression_log.txt')

def log_message(message):
    """Append a message to the log file."""
    with open(LOG_FILE_PATH, 'a') as log_file:
        log_file.write(message + '\n')

@receiver(post_save, sender=TweetPostImagesModel)
def compress_media(sender, instance, **kwargs):
    # Write to log when signal is triggered
    log_message(f"Signal triggered for instance {instance.pk} at {now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if instance.image:  # Compress image if present
        compress_image(instance.image.path)

    if instance.video:  # Compress video if present
        compress_video(instance.video.path)

def compress_image(image_path):
    with Image.open(image_path) as img:
        # Adjust the quality of the image here (1-100)
        img.save(image_path, optimize=True, quality=50)
    log_message(f"Image compressed: {image_path}")

import sys
import contextlib
from moviepy.editor import VideoFileClip

@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__

def compress_video(video_path):
    try:
        clip = VideoFileClip(video_path)
        target_bitrate = "500k"
        temp_video_path = video_path + "_temp.mp4"
        
        # Open the log file in append mode
        with open(LOG_FILE_PATH, 'a') as log_file, stdout_redirect(log_file):
            # The output of moviepy will be redirected to log_file
            clip.write_videofile(temp_video_path, bitrate=target_bitrate)
            log_file.flush()  # Ensure all data is flushed to the file

        # Replace original with compressed
        os.replace(temp_video_path, video_path)
        
        # Write a completion message to the log file
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Video compressed and saved to: {video_path}\n")
        
    except Exception as e:
        # Write an error to the log file
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"Error compressing video {video_path}: {e}\n")
