from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status , generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    UnFollowModelDestroySerializer,FollowersModelListSerializer,FollowingModelListSerializer,FollowModelListSerializer,
    FollowModelCreateSerializer,FollowModelRetrieveSerializer,RequestToFollowSerializer,RequestToFollowStatusUpdateSerializer
)
from following_system.models import FollowModel,RequestToFollow


User = get_user_model()





class RequestToFollowCreateAPIView(generics.CreateAPIView):
    queryset = RequestToFollow.objects.all()
    serializer_class = RequestToFollowSerializer



class RequestToFollowUpdateAPIView(generics.UpdateAPIView):
    queryset = RequestToFollow.objects.all()
    serializer_class = RequestToFollowStatusUpdateSerializer
    def update(self, request, *args, **kwargs):
        request_to_follow_id = kwargs.get('id')  # Get the ID from the URL
        try:
            request_to_follow = RequestToFollow.objects.get(pk=request_to_follow_id)
        except RequestToFollow.DoesNotExist:
            return Response({"error": "RequestToFollow not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(request_to_follow, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
        
        

class FollowersModelUsersListView(generics.ListAPIView):
    serializer_class = FollowersModelListSerializer
    
    def get_queryset(self):
        user_id = self.kwargs.get('id')  # Get the user_id from URL parameters
        user_follow_model_obj, created = FollowModel.objects.get_or_create(user_id=user_id)
        return user_follow_model_obj  # Return the specific user's FollowModel object

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request})
        return Response({'success': True, 'user_data': serializer.data})

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class FollowingModelUserListView(generics.ListAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = FollowingModelListSerializer
    def get_queryset(self):
        user = self.kwargs.get('id')  # Assuming you want the APIs for the currently authenticated user
        user_follow_model_obj, created = FollowModel.objects.get_or_create(user=user)
        return user_follow_model_obj  # Return the specific user's FollowModel object

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request})
        return Response({'success': True, 'user_data': serializer.data})



class FollowingModelListView(generics.ListAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = FollowingModelListSerializer
    def get_queryset(self):
        user = self.request.user  # Assuming you want the APIs for the currently authenticated user
        user_follow_model_obj, created = FollowModel.objects.get_or_create(user=user)
        return user_follow_model_obj  # Return the specific user's FollowModel object

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request})
        return Response({'success': True, 'user_data': serializer.data}) # Correct response format

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class FollowersModelListView(generics.ListAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = FollowersModelListSerializer
    def get_queryset(self):
        user = self.request.user  # Assuming you want the APIs for the currently authenticated user
        user_follow_model_obj, created = FollowModel.objects.get_or_create(user=user)
        return user_follow_model_obj  # Return the specific user's FollowModel object

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request})
        return Response({'success': True, 'user_data': serializer.data})  # Correct response format

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class FollowModelCreateView(generics.CreateAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = FollowModelCreateSerializer
    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        # Pass the user_id to the serializer context
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs.get('id')
        
        print(context)
        return context
    

class UnFollowModelCreateView(generics.CreateAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = UnFollowModelDestroySerializer
    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self):
        # Pass the user_id to the serializer context
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs.get('id')
        return context



class FollowModelRetrieveView(generics.RetrieveAPIView):
    queryset = FollowModel.objects.all()
    serializer_class = FollowModelRetrieveSerializer
    def get_object(self):
        # Customize how you retrieve the object, e.g., filter by user and followed_user
        return FollowModel.objects.get(user=self.request.user, followers=self.kwargs['pk'])
