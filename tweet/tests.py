from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from tweet.models import Tweet

# Create your tests here.
class TweetTestCase(TestCase):
    User = User.objects.all()
    def setUp(self):
        self.user = User.objects.create_user(username='abc',password='1237')
        tweet_obj = Tweet.objects.create(content="hey there", user=self.user)
        tweet_obj = Tweet.objects.create(content="hey there", user=self.user)
        tweet_obj = Tweet.objects.create(content="hey there", user=self.user)
        tweet_obj = Tweet.objects.create(content="hey there", user=self.user)



    def test_tweet_created(self):
        tweet_obj = Tweet.objects.create(content="hey there",user=self.user)
        self.assertEqual(tweet_obj.id,5)
        self.assertEqual(tweet_obj.user, self.user)

    def get_client(self):
        client = APIClient()
        client.login(username=self.user.username, password='1237')
        return client

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get("/api/tweet/list/")
        # print(response.json())

    def test_tweet_create_api(self):
        data = {"content": "hi, who are you"}
        client = self.get_client()
        response =client.post("/api/tweet/create/",data)
        self.assertEqual(response.status_code,201)


    def test_tweet_detail_api(self):
        client = self.get_client()
        response =client.get("/api/tweet/1/")
        self.assertEqual(response.status_code,200)
        data=response.json()

    def test_tweet_delete_api(self):
        client = self.get_client()
        response =client.delete("/api/tweet/1/delete/")
        self.assertEqual(response.status_code,200)
        client = self.get_client()
        response =client.delete("/api/tweet/1/delete/")
        self.assertEqual(response.status_code,404)