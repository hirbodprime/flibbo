from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from posts.models import TweetPostModel  

User = get_user_model()
from accounts.models import CustomUser
class TweetPostAPITestCase(APITestCase):
    def setUp(self):
        # Create the user with username 'hirbod'
        self.user = CustomUser.objects.create_user(
            email='hirbodprime@gmail.com',
            full_name='hirbod aflaki',
            password='keyhan1234',
            # Add other required fields if necessary
        )
        self.create_url = reverse('tweet_create')  # Adjust as necessary
        login_successful = self.client.login(email='hirbodprime@gmail.com', password='keyhan1234')
        assert login_successful, "Login failed in test setup"


    def test_create_tweet_post(self):
        # Define the data for a new tweet post
        data = {
            'caption': 'Test Caption',
            'location': 'TestLocation',

        }


        # Make a POST request to create a new tweet post
        response = self.client.post(self.create_url, data, format='json')
        print(response.data)  # Add this line to debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        # Retrieve the created tweet post
        tweet_post = TweetPostModel.objects.last()

        # Check that the logged-in user is set as the author of the tweet post
        self.assertEqual(tweet_post.user, self.user)

        # Additional checks can be performed here for other fields
