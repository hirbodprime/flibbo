from django.core.management.base import BaseCommand
from posts.models import TweetPostModel  # Replace 'myapp' with the actual app name
from django.core.files.base import ContentFile
import os

class Command(BaseCommand):
    help = 'Compresses videos in TweetPostModel'

    def handle(self, *args, **kwargs):
        for post in TweetPostModel.objects.all():
            if post.video:
                print(f"Compressing video for post {post.id}")

                # Compress the video
                compressed_video_path = post.compress_video(post.video.path)

                # Update post.video with the compressed video
                with open(compressed_video_path, 'rb') as f:
                    post.video.save(os.path.basename(compressed_video_path), ContentFile(f.read()), save=False)

                # Clean up the temp file
                os.remove(compressed_video_path)

                print(f"Finished compressing video for post {post.id}")
