from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

from category.models import UserFavoriteCategories,CategoryModel
from posts.models import TweetPostModel, PodcastPostModel
from posts.api.serializers import TweetPostSerializer, PodcastPostSerializer
from explore.custom_pagination import CustomPagination
from accounts.models import BlockModel

from django.db.models import F, Count,Q



class ExploreViewApi(APIView):
    def get(self, request):
        try:
            # Querying tweets ordered by view count and creation date
            tweets = TweetPostModel.objects.filter(
                user__private=False,
                hide=False
            ).annotate(
                view_count=Count('viewed_by_users')
            ).order_by('-view_count', '-created_date')

            # Use only select_related() or prefetch_related() as needed
            tweets = tweets.select_related('user').prefetch_related('category')

            # Pagination
            paginator = CustomPagination()
            paginated_tweets = paginator.paginate_queryset(tweets, request)

            if not paginated_tweets and request.query_params.get('page', '1') != '1':
                return Response({'success': True, 'data': 'No more tweets available'}, status=status.HTTP_200_OK)

            # Bulk serialization
            tweet_data = TweetPostSerializer(paginated_tweets, many=True, context={'request': request}).data

            # Building response
            response_data = {
                "tweets": tweet_data,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }

            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for more detailed error tracking
            # logger.error("Error in ExploreViewApi: %s", str(e))
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class ExploreViewApi(APIView):
#     def get(self, request):
#         paginator = CustomPagination()
#         # paginator.page_size = 30  # Set page size
#         user = request.user  # Assuming the user is authenticated
        
#         block_obj,created = BlockModel.objects.get_or_create(user=user)
#         users_blocked_by_current_user = block_obj.blocked_users.all()

#         # Step 2: Get users who have blocked the current user
#         users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=user)
#         blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
#         # Step 3: Combine the lists
#         blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        
#         user_categorymodel_obj, _ = UserFavoriteCategories.objects.get_or_create(user=user)

#         try:
#             categories = user_categorymodel_obj.favorite_categories.all()

#             tweets = TweetPostModel.objects.exclude(user__in=blocked_users_combined).filter(
#                 category__in=categories,
#                 user__private=False,
#                 hide=False
#             ).annotate(view_count=Count('viewed_by_users')).order_by('-view_count', '-created_date')
            
#             if not tweets.exists():  # Check if the filtered queryset is empty
#                 return Response({'success': True, 'data': 'No tweets available'}, status=status.HTTP_200_OK)

#             paginated_tweets = paginator.paginate_queryset(tweets, request)
            
#             if not paginated_tweets and request.query_params.get('page', '1') != '1':
#                 return Response({'success': True, 'data': 'No more tweets available'}, status=status.HTTP_200_OK)

#             tweet_data = [TweetPostSerializer(tweet, context={'request': request}).data for tweet in paginated_tweets]

#             response_data = {
#                 "tweets": tweet_data,
#                 'next': paginator.get_next_link(),
#                 'previous': paginator.get_previous_link(),
#             }

#             return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExploreCategoriesViewApi(APIView):
    def get(self, request, category_name):
        user = request.user  # Assuming the user is authenticated
        paginator = CustomPagination()
        block_obj,created = BlockModel.objects.get_or_create(user=user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        # paginator.page_size = 1
        try:
            # Query the CategoryModel to get the category by name
            category = CategoryModel.objects.get(slug=category_name)
            
            # Annotate the count of likes for each tweet in the selected category
            tweets = TweetPostModel.objects.exclude(user__in=blocked_users_combined).filter(category=category,user__private=False).annotate(like_count=Count('likes')).order_by('-like_count', '-created_date')
            paginated_tweets = paginator.paginate_queryset(tweets, request)
            tweet_data = [TweetPostSerializer(tweet, context={'request': request}).data for tweet in paginated_tweets]
            
            # Combine the serialized data into a single response
            response_data = {
                "tweets": tweet_data,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link()
            }
            
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        except CategoryModel.DoesNotExist:
            return Response({'success': False, 'message': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)






# class ExploreViewApi(APIView):
#     def get(self, request):
#         user = request.user  # Assuming the user is authenticated
#         user_categorymodel_obj = UserFavoriteCategories.objects.get_or_create(user=user)
#         print(user_categorymodel_obj)
#         try:
#             categories = user_categorymodel_obj[0].favorite_categories.all()
            
#             # Annotate the count of likes for each tweet
#             tweets = TweetPostModel.objects.filter(category__in=categories).annotate(like_count=Count('likes')).order_by('-created_date', '-like_count')
#             tweet_data = [TweetPostSerializer(tweet, context={'request': request}).data for tweet in tweets]
            
#             # Annotate the count of likes for each podcast
#             podcasts = PodcastPostModel.objects.filter(category__in=categories).annotate(like_count=Count('likes')).order_by('-created_date', '-like_count')
#             podcast_data = [PodcastPostSerializer(podcast, context={'request': request}).data for podcast in podcasts]
            
#             # Combine the serialized data into a single response
#             response_data = {
#                 "tweets": tweet_data,
#                 "podcasts": podcast_data,
#             }
            
#             return Response({'success':True,'data':response_data}, status=status.HTTP_200_OK)
#         except:
#             return Response({'success':False}, status=status.HTTP_200_OK)
