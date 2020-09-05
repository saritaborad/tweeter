from django.urls import path,include
from .views import *


urlpatterns = [
    # tweet related urls
    path('create/',TweetCreateView.as_view()),
    path('list/',TweetListView.as_view()),
    path('feed/',TweetFeedView.as_view()),
    path('<int:pk>/',TweetDetailAPIView.as_view(),name='detail'),
    path('<int:pk>/delete/',TweetDeleteView.as_view()),
    path('action/',TweetActionView.as_view()),
    path('comment/',CommentView.as_view()),
    path('reply/',ReplyView.as_view()),
    path('follow/<str:username>/',user_follow_view),

]