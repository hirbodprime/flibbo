from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from django.shortcuts import render
from django.http import HttpResponse
from .extract_ip import get_user_ip



class FCMDeviceViewSet(FCMDeviceAuthorizedViewSet):
    pass




def get_user_ip_view(request):
    user_ip = get_user_ip(request)
    return HttpResponse(f"Your IP address is {user_ip}")