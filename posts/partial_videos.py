from django.http import StreamingHttpResponse, HttpResponseBadRequest, JsonResponse
from .models import TweetPostModel
import os

def file_iterator(file_path, start, end, chunk_size=8192):
    with open(file_path, 'rb') as file:
        file.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            bytes_to_read = min(remaining, chunk_size)
            data = file.read(bytes_to_read)
            if not data:
                break
            yield data
            remaining -= len(data)

def serve_video(request, post_id):
    try:
        post = TweetPostModel.objects.get(id=post_id)
    except TweetPostModel.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    if not post.video:
        return JsonResponse({'error': 'No video found for this post'}, status=404)

    file_path = post.video.path
    file_size = os.path.getsize(file_path)

    range_header = request.META.get('HTTP_RANGE')
    if range_header:
        start, end = range_header.strip().split("=")[1].split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        response = StreamingHttpResponse(file_iterator(file_path, start, end), status=206, content_type='video/mp4')
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        return response

    # Fallback for non-range requests
    return StreamingHttpResponse(file_iterator(file_path, 0, file_size - 1), content_type='video/mp4')
