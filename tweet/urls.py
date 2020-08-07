from django.urls import path,include
from .views import *


urlpatterns = [
    # tweet related urls
    path('create/',tweet_create_view),
    path('list/',tweet_list_view),
    path('feed/',tweet_feed_view),
    path('<int:pk>/',TweetDetailAPIView.as_view(),name='detail'),
    path('<int:tweet_id>/delete/',tweet_delete_view),
    path('action/',tweet_like_view),
    path('comment/',CommentView.as_view()),


    #  user related urls
    path('follow/<str:username>/',user_follow_view),
    path('register/',UserCreateApiView.as_view(),name='register'),
    path('login/',UserLoginAPIView.as_view(),name='login'),
    path('password-reset/<uidb64>/<token>/',PasswordTokenCheckAPIView.as_view(),name='password-reset'),
    path('pasword-reset-request/',PasswrodResetAPIView.as_view(),name='request-email'),
    path('set-password/',SetNewPasswordAPIView.as_view(),name='set-new-passwrod'),

]






































































































































































