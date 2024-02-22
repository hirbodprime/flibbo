from moviepy.editor import VideoFileClip
import requests
from django.core.files.base import ContentFile
import os

def extract_and_save_cover(video_url, model_instance):
    print("videl url in cover: ", video_url)
    from .models import TalkResponse  # Import your model
    video_filename = None
    image_filename = None
    try:
        # Download the video file from the URL
        response = requests.get(video_url)
        video_filename = "temp_video.mp4"
        with open(video_filename, 'wb') as file:
            file.write(response.content)

        # Load the video file and extract the first frame
        clip = VideoFileClip(video_filename)
        frame = clip.get_frame(0)  # Gets the first frame

        # Convert frame to image file
        image_filename = "cover.jpg"
        clip.save_frame(image_filename, t=0)  # t=0 saves the first frame

        # Save the image to your model
        with open(image_filename, 'rb') as img_file:
            model_instance.cover_image.save(image_filename, ContentFile(img_file.read()), save=True)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if video_filename and os.path.exists(video_filename):
            os.remove(video_filename)
        if image_filename and os.path.exists(image_filename):
            os.remove(image_filename)
