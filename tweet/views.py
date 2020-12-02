from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from tweet.utils import SendMail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.urls import reverse
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view,permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import (IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly)
from tweet.models import Tweet,Comment
from tweet.serializers import *


class TweetDetailAPIView(GenericAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]

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
            serializer = self.serializer_class(obj,many=False)
            return Response(serializer.data,status=200)
        return Response({'error':'Given tweet not found'},status=404)

    def put(self,request,pk=None):
        data=request.data
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=404)

    def delete(self,request,pk=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response('tweet deleted')

class TweetCreateView(GenericAPIView):
    serializer_class = TweetCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=200)
        return Response({'message': 'something went wrong!!'}, status=400)



class TweetFeedView(GenericAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Tweet.objects.all()

    def get(self,request,*args,**kwargs):
        user = request.user
        profiles_exist = user.following.exists()
        follow_user_id = []
        if profiles_exist or User.objects.filter(username=user):
            follow_user_id = user.following.values_list('user__id', flat=True)
            qs = self.get_queryset()
            qs.filter(Q(user__id__in=follow_user_id) | Q(user=user)).distinct().order_by("-timestamp")
            serializer = self.serializer_class(qs,many=True)
            return Response(serializer.data)

        return Response('no data found')


class TweetListView(GenericAPIView):
    serializer_class = TweetSerializer
    queryset = Tweet.objects.all()


    def get(self,request,*args,**kwargs):
        qs = self.get_queryset()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class TweetDeleteView(GenericAPIView):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Tweet.objects.all()

    def get_object(self,pk):
        try:
            qs = self.queryset.filter(id=pk)
            if qs.exists():
                return qs.first()
        except Tweet.DoesNotExist:
            return Response({'error': 'Given tweet not found'}, status=404)

    def get(self, request, pk=None):
        obj = self.get_object(pk)
        if obj:
            serializer = self.serializer_class(obj, many=False)
            return Response(serializer.data, status=200)
        return Response({'error': 'Given tweet not found'}, status=404)

    def delete(self,request,pk=None,*args,**kwargs):
        obj = self.get_object(pk)
        if obj.user == request.user:
            obj.delete()
            return Response('tweet deleted',status=200)
        return Response({'message':'you cannot delete this tweet'})


class TweetActionView(GenericAPIView):
    serializer_class = TweetActionSerializer
    serializer_action_class = TweetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Tweet.objects.all()

    def post(self,request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            tweet_id = data.get('id')
            action = data.get('action')
            content = data.get('content')

            qs = self.queryset.filter(id=tweet_id)
            if not qs.exists():
                return Response({'Invalid data'}, status=404)
            obj = qs.first()
            if action == 'like':
                obj.likes.add(request.user)
                serializer = self.serializer_action_class(obj)
                return Response(serializer.data, status=200)
            elif action == 'unlike':
                obj.likes.remove(request.user)
                return Response({'msg':'like removed'},status=200)
            elif action == 'retweet':
                parent_obj = obj
                new_tweet = Tweet.objects.create(user=request.user, parent_id=parent_obj.id, content=content)
                serializer = self.serializer_action_class(new_tweet)
                return Response(serializer.data, status=200)


class CommentView(GenericAPIView):

    queryset = Comment.objects.filter(reply_parent_id=None)
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


class ReplyView(GenericAPIView):

    serializer_class = ReplySerializer

    def get_object(self,pk):
        try:
            obj = Reply.objects.filter(id=pk)
            if obj.exists():
                return obj.first()
        except Reply.DoesNotExist:
            return Response('Reply is not found',status=404)

    def get(self,pk=None,*args,**kwargs):
        obj = self.get_object(pk)
        if obj:
            serializer = self.serializer_class(obj, many=False)
            return Response(serializer.data, status=200)
        return Response({'error': 'Given reply not found'}, status=404)


    def put(self,request,pk=None,*args,**kwargs):
        obj = self.get_object(pk)
        serializer = ReplyActionSerializer(obj,data=request.data)
        if serializer.is_valid:
            serializer.save()
            return Response(serializer.data,status=200)
        return Response('data is invalid',status=404)

    def delete(self,pk=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response('Reply is deleted successfully',status=200)

    def post(self, request,*args,**kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            tweet = data.get('tweet')
            comment = data.get('reply_parent')
            content = data.get('content')
            qs = Comment.objects.filter(id=comment.id)
            if not qs.exists():
                return Response({'Invalid data'}, status=404)
            obj = qs.first()
            parent_obj = obj
            reply = Comment.objects.create(tweet_id=tweet.id,user=request.user,reply_parent_id=parent_obj.id, content=content)
            serializer = self.serializer_class(reply)
            return Response(serializer.data, status=200)


class UserFollowView(GenericAPIView):

    def get(self,request,username,*args,**kwargs):
        me = request.user
        other_user = User.objects.filter(username=username)
        if me.username == username:
            my_follower = me.profile.followers.all()
            return Response({'followers': my_follower.count()}, status=200)

        if not other_user.exists():
            return Response({'No such user exists'}, status=404)

    def post(self,request,username,*args,**kwargs):
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

