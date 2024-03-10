from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from posts.models import TweetPostModel
from activity.models import Activity
from .serializers import ActivitySerializer, ActivitySerializerV2
from following_system.models import RequestToFollow 
from following_system.api.serializers import RequestToFollowListSerializer
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed(request, activity_type_url):
    if activity_type_url == 'follow':
        activity_type_values = Activity.objects.filter(activity_type=activity_type_url).values_list('activity_type', flat=True)
        follower_activities = Activity.objects.filter(Q(activity_type=Activity.FOLLOW, followed_user=request.user)).order_by('-created_at')
        request_activities = RequestToFollow.objects.filter(requset_reciever=request.user).order_by('-created_at')
        serializer_requests = RequestToFollowListSerializer(instance=request_activities, context={'request': request}, many=True)
        serializer = ActivitySerializer(instance=follower_activities, context={'request': request}, many=True)
        response_data = {
        'data':serializer.data,
        'requests':serializer_requests.data
        }
        return Response(response_data)
    # Extract activity_type values from the queryset
    activity_type_values = Activity.objects.filter(activity_type=activity_type_url).values_list('activity_type', flat=True)
    
    user_posts = TweetPostModel.objects.filter(user=request.user)
    
    # Query activities related to the user's own tweets
    user_activities = Activity.objects.filter(Q(tweet__in=user_posts, activity_type__in=activity_type_values)).order_by('-created_at')

    serializer = ActivitySerializer(instance=user_activities, context={'request': request}, many=True)
    response_data = {
        'data':serializer.data
    }
    return Response(response_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed_v2(request, category):
    # Define category to activities mapping
    category_mappings = {
        'engagement': [Activity.LIKE, Activity.COMMENT, Activity.SAVE],
        'requests': [Activity.FOLLOW, Activity.UNFOLLOW],
        'tags': [Activity.TAG],
    }

    user_posts_ids = TweetPostModel.objects.filter(user=request.user).values_list('id', flat=True)

    # Adjusting the activities query
    # This fetches activities related to the user's posts and where the user is the followed_user
    activities = Activity.objects.filter(
        Q(tweet__in=user_posts_ids) |
        Q(followed_user=request.user)
    ).distinct().order_by('-created_at')
    
    
    if category == 'all':
        # Split the queryset into newest and oldest
        newest_activities = activities[:10]  # The 10 most recent activities
        oldest_activities = activities[10:]  # The rest of the activities
        
        # Serializing the activities
        newest_serializer = ActivitySerializerV2(instance=newest_activities, context={'request': request}, many=True)
        oldest_serializer = ActivitySerializerV2(instance=oldest_activities, context={'request': request}, many=True)
        
        response_data = {
            'newest': newest_serializer.data,
            'oldest': oldest_serializer.data,
        }
        return Response(response_data)

    elif category in category_mappings:
        # Filter activities based on the selected category
        activities = activities.filter(activity_type__in=category_mappings[category])

        # Serializing the activities
        serializer = ActivitySerializerV2(instance=activities, context={'request': request}, many=True)
        return Response({'data': serializer.data})

    else:
        return Response({"error": "Invalid category provided"}, status=400)
