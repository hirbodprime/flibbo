from django.core.management.base import BaseCommand
from posts.models import TweetPostModel
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

class Command(BaseCommand):
    help = 'Compresses all photos in TweetPostModel'

    def handle(self, *args, **kwargs):
        for tweet_post in TweetPostModel.objects.filter(photo__isnull=False):
            # Check if an image file exists
            if tweet_post.photo:  # This checks if photo is not None and file exists
                try:
                    # Open the existing image
                    pil_image = Image.open(tweet_post.photo)

                    # Convert RGBA to RGB if needed
                    if pil_image.mode == 'RGBA':
                        pil_image = pil_image.convert('RGB')

                    # Compress the image
                    output_io_stream = io.BytesIO()
                    pil_image.save(output_io_stream, format='JPEG', quality=70)
                    output_io_stream.seek(0)

                    # Replace the existing image with the compressed one
                    tweet_post.photo = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                            "%s.jpg" % tweet_post.photo.name.split('.')[0], 
                                                            'image/jpeg', 
                                                            output_io_stream.getbuffer().nbytes, 
                                                            None)
                    tweet_post.save()

                    self.stdout.write(self.style.SUCCESS(f'Compressed photo for tweet post {tweet_post.id}'))

                except IOError:
                    self.stdout.write(self.style.ERROR(f'Error processing photo for tweet post {tweet_post.id}'))
