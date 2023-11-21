# views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import generics
from notification.models import UserDeviceModel
from .serializers import UserDeviceModelSerializer
from rest_framework import generics, status
from rest_framework.response import Response


@api_view(['GET'])
def user_device_list(request):
    if request.method == 'GET':
        devices = UserDeviceModel.objects.all()
        serializer = UserDeviceModelSerializer(devices, many=True)
        return JsonResponse(serializer.data, safe=False)

# views.py

class UserDeviceListCreateView(generics.ListCreateAPIView):
    # queryset = UserDeviceModel.objects.all()
    serializer_class = UserDeviceModelSerializer
    def get_queryset(self):
        return UserDeviceModel.objects.filter(user=self.request.user)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserDeviceModelSerializer(queryset, many=True)
        return Response({'devices': serializer.data})

    def create(self, request, *args, **kwargs):
        # Try to find an existing device for this user
        instance = UserDeviceModel.objects.filter(user=request.user).first()

        # Initialize the serializer with the existing instance (if found)
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            if instance:
                serializer.save()  # Update the existing instance
                return Response({'device': serializer.data}, status=status.HTTP_200_OK)
            else:
                self.perform_create(serializer)  # Create a new instance
                headers = self.get_success_headers(serializer.data)
                return Response({'device': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeviceUpdateView(generics.UpdateAPIView):
    queryset = UserDeviceModel.objects.all()
    serializer_class = UserDeviceModelSerializer
    lookup_field = 'pk'  # or any other field that uniquely identifies a record