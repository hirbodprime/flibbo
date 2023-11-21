from posts.models import TweetPostModel, BookPostModel, PodcastPostModel, TweetCommentModel
from activity.models import Activity
from accounts.models import SavedByUser


def increment_views_count_tweets(post_id, user):
    try:
        posts = TweetPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.viewed_by_users.all():
                Activity.objects.create(user=user, tweet=post, activity_type=Activity.VIEW)
                post.increment_total_views()
                post.increment_view_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found





def increment_saves_count_tweets(post_id, user):
    try:
        posts = TweetPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.saved_by_users.all():
                Activity.objects.create(user=user, tweet=post, activity_type=Activity.SAVE)
                post.increment_total_saves()
                post.increment_save_users(user)  # Use add to add the user to the ManyToMany field
                saved_by_user, created = SavedByUser.objects.get_or_create(user=user)
                saved_by_user.saved_tweets.add(post) 
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found



def increment_likes_count_tweets(post_id, user):
    try:
        posts = TweetPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.likes.all():
                Activity.objects.create(user=user, tweet=post, activity_type=Activity.LIKE)

                post.increment_total_likes()
                post.increment_like_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found



def dicrement_saves_count_tweets(post_id, user):
    try:
        posts = TweetPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user in post.saved_by_users.all():
                Activity.objects.create(user=user, tweet=post, activity_type=Activity.UNSAVE)
                post.dicrement_total_saves()
                post.dicrement_save_users(user)  # Use add to add the user to the ManyToMany field
                saved_by_user, created = SavedByUser.objects.get_or_create(user=user)
                saved_by_user.saved_tweets.remove(post) 
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found



def dicrement_likes_count_tweets(post_id, user):
    try:
        posts = TweetPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user in post.likes.all():
                Activity.objects.create(user=user, tweet=post, activity_type=Activity.UNLIKE)
                post.dicrement_total_likes()
                post.dicrement_like_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found



def increment_likes_count_tweet_comments(comment_id, user):
    try:
        posts = TweetCommentModel.objects.filter(id__in=comment_id)
        for post in posts:
            if user not in post.likes.all():
                Activity.objects.create(user=user, tweet_comment=post, activity_type=Activity.COMMENT)

                post.increment_total_likes()
                post.increment_like_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found

def dicrement_likes_count_tweets_comments(comment_id, user):
    try:
        posts = TweetCommentModel.objects.filter(id__in=comment_id)
        for post in posts:
            if user in post.likes.all():
                Activity.objects.create(user=user, tweet_comment=post, activity_type=Activity.UNCOMMENT)

                post.dicrement_total_likes()
                post.dicrement_like_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found




def increment_views_count_podcasts(post_id, user):
    try:
        posts = PodcastPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.viewed_by_users.all():
                post.increment_total_views()
                post.increment_view_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                return False  # User already added
        return True  
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found

def increment_saves_count_podcasts(post_id, user):
    try:
        posts = PodcastPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.saved_by_users.all():
                post.increment_total_saves()
                post.increment_save_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                return False  # User already added
        return True  
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found

def increment_likes_count_podcasts(post_id, user):
    try:
        posts = PodcastPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user not in post.likes.all():
                post.increment_total_likes()
                post.increment_like_users(user)   # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                return False  # User already added
        return True  
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found


def dicrement_saves_count_podcasts(post_id, user):
    try:
        posts = PodcastPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user in post.saved_by_users.all():
                post.dicrement_total_saves()
                post.dicrement_save_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found



def dicrement_likes_count_podcasts(post_id, user):
    try:
        posts = PodcastPostModel.objects.filter(id__in=post_id)
        for post in posts:
            if user in post.likes.all():
                post.dicrement_total_likes()
                post.dicrement_like_users(user)  # Use add to add the user to the ManyToMany field
            else:
                print('User is in the view')
                # return False  # User already added
        return True  
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found

        












def increment_views_count_tweet(post_id, user):
    try:
        post = TweetPostModel.objects.get(id=post_id)
        if user not in post.viewed_by_users.all():
            post.increment_total_views()
            post.increment_view_users(user)  # Use add to add the user to the ManyToMany field
            return True  # Indicate success
        else:
            print('User is in the view')
            return False  # User already added
    except TweetPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found


def increment_views_count_book(post_id, user):
    try:
        post = BookPostModel.objects.get(id=post_id)
        if user not in post.viewed_by_users.all():
            post.increment_total_views()
            post.increment_view_users(user)  # Use add to add the user to the ManyToMany field
            return True  # Indicate success
        else:
            print('User is in the view')
            return False  # User already added
    except BookPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found


def increment_views_count_podcast(post_id, user):
    try:
        post = PodcastPostModel.objects.get(id=post_id)
        if user not in post.viewed_by_users.all():
            post.increment_total_views()
            post.increment_view_users(user)  # Use add to add the user to the ManyToMany field
            return True  # Indicate success
        else:
            print('User is in the view')
            return False  # User already added
    except PodcastPostModel.DoesNotExist:
        print('Post does not exist')
        return False  # Post not found
