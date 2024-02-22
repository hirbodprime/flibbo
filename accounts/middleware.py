import requests
from django.conf import settings
class CheckHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_host = request.get_host()

        if current_host != 'app.flxdevpanel.com':
            # If the current host doesn't match the target host, send a request to the redirect URL
            # requests.get('https://app.flxdevpanel.com/posts/api/podcast/notifs/1/')
            requests.get(f"{settings.SITE_DOMAIN}/posts/api/podcast/notifs/1/")


        response = self.get_response(request)
        return response
