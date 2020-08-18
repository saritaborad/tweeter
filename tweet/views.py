from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from tweet.utils import SendMail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly)
from tweet.models import Tweet,Comment
from tweet.serializers import *

class TweetDetailAPIView(APIView):
    def get_object(self,pk):
        try:
            qs = Tweet.objects.filter(id=pk)
            if qs.exists():
                return qs.first()
        except Tweet.DoesNotExist:
            return Response({'error':'Given tweet not found'},status=404)

    def get(self,request,pk=None):
        obj =self.get_object(pk)
        if obj:
            serializer = TweetSerializer(obj,context={'request': request},many=False)
            return Response(serializer.data,status=200)
        return Response({'error':'Given tweet not found'},status=404)

    def put(self,request,pk=None):
        data=request.data
        obj = self.get_object(pk)
        serializer = TweetSerializer(obj,context={'request': request},data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=404)

    def delete(self,request,pk=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response('tweet deleted')

class TweetCreateView(generics.GenericAPIView):
    serializer_class = TweetCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=200)
        return Response({'message': 'something went wrong!!'}, status=400)


from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tweet_feed_view(request,*args,**kwargs):
    user = request.user
    qs = Tweet.objects.feed(user)
    serializer = TweetSerializer(qs,context={'request': request},many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tweet_list_view(request,*args,**kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs,context={'request': request},many=True)
    return Response(serializer.data)


@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request,tweet_id,*args,**kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({'tweet does not exists'},status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({'message':'you cannot delete this tweet'})
    obj = qs.first()
    obj.delete()
    return Response({'message':'tweet removed'},status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_like_view(request,*args,**kwargs):
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        tweet_id = data.get('id')
        action = data.get('action')
        content = data.get('content')

        qs = Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({'Invalid data'},status=404)
        obj = qs.first()
        if action == 'like':
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj,context={'request': request})
            return Response(serializer.data,status=200)
        elif action == 'unlike':
            obj.likes.remove(request.user)
        elif action == 'retweet':
            parent_obj = obj
            new_tweet = Tweet.objects.create(user=request.user,parent=parent_obj,content=content)
            serializer = TweetSerializer(new_tweet,context={'request': request})
            return Response(serializer.data,status=200)


class CommentView(generics.GenericAPIView):
    # queryset = Comment.objects.filter(parent=None) # Don't
    queryset = Comment.objects.all()

    serializer_class = CommentSerializer

    def get(self, request):
        qs = self.get_queryset()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=200)
        return Response({'message': 'something went wrong!!'}, status=400)


class ReplyView(generics.GenericAPIView):

    serializer_class = ReplySerializer

    def post(self, request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            tweet = data.get('tweet')
            content = data.get('content')
            parent = data.get('reply_parent')
            qs = Comment.objects.filter(id=parent.id)
            if not qs.exists():
                return Response({'Invalid data'}, status=404)
            obj = qs.first()
            parent_obj = obj
            reply = Comment.objects.create(user=request.user, reply_parent_id=parent_obj.id, content=content,tweet=tweet)
            serializer = ReplySerializer(reply)
            return Response(serializer.data, status=200)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_follow_view(request, username, *args, **kwargs):
    me = request.user
    other_user = User.objects.filter(username=username)
    if me.username == username:
        my_follower = me.profile.followers.all()
        return Response({'followers': my_follower.count()}, status=200)

    if not other_user.exists():
        return Response({}, status=404)
    other = other_user.first()
    profile = other.profile
    data = request.data or {}
    action = data.get('action')
    if action == 'follow':
        profile.followers.add(me)
    elif action == 'unfollow':

        profile.followers.remove(me)
    else:
        pass
    current_follower = profile.followers.all()
    return Response({'followers': current_follower.count()}, status=200)

