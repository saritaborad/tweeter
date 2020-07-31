from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .utils import SendMail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.urls import reverse

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK,HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.decorators import api_view,permission_classes
from rest_framework import generics
from rest_framework.permissions import (IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly)
from .models import Tweet
from .serializers import *

class TweetDetailAPIView(APIView):
    def get_object(self,id):
        try:
            qs = Tweet.objects.filter(id=id)
            if qs.exists():
                return qs.first()
        except Tweet.DoesNotExist:
            return Response({'error':'Given tweet not found'},status=404)

    def get(self,request,id=None):
        obj =self.get_object(id)
        if obj:
            serializer = TweetSerializer(obj,many=False)
            return Response(serializer.data,status=200)
        return Response({'error':'Given tweet not found'},status=404)

    def put(self,request,id=None):
        data=request.data
        obj = self.get_object(id)
        serializer = TweetSerializer(obj,data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=404)

    def delete(self,request,id=None):
        obj = self.get_object(id)
        obj.delete()
        return Response('tweet deleted')



# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetCreateSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data,status=201)
    return Response({}, status=400)

from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tweet_feed_view(request,*args,**kwargs):
    user = request.user
    qs = Tweet.objects.feed(user)
    serializer = TweetListSerializer(qs,context={'request': request},many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tweet_list_view(request,*args,**kwargs):
    qs = Tweet.objects.all()
    serializer = TweetListSerializer(qs,context={'request': request},many=True)
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
            serializer = TweetSerializer(obj)
            return Response(serializer.data,status=200)
        elif action == 'unlike':
            obj.likes.remove(request.user)
        elif action == 'retweet':
            parent_obj = obj
            new_tweet = Tweet.objects.create(user=request.user,parent=parent_obj,content=content)
            serializer = TweetSerializer(new_tweet)
            return Response(serializer.data,status=200)


class UserCreateApiView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            new_data = serializer.data
            return Response(new_data,status=HTTP_200_OK)
        return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)

class PasswrodResetAPIView(generics.GenericAPIView):
    serializer_class = PasswrodResetSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset',kwargs={'uidb64':uidb64,'token':token})
            absurl ='http://'+ current_site +relativeLink
            email_body = 'Hi '+user.username+'\n Use link below to reset your password\n' + absurl
            data = {'email_body':email_body,'to_email':user.email,'email_subject':'reset your password'}
            SendMail.send_mail(data)
        return Response({'success':'we have sent you link to reset password'})


class PasswordTokenCheckAPIView(generics.GenericAPIView):

    def get(self,request,uidb64,token):
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user =User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({'error':'Token is invalid, please generate new'},status=401)
            return Response({'success':True,'message':'credential valid','uidb64':uidb64,'token':token},status=200)
        except DjangoUnicodeDecodeError as identifier:
            print(identifier)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        return Response({'success':True,'message':'Password reset success'},status=200)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def user_follow_view(request,username,*args,**kwargs):
    me = request.user
    other_user = User.objects.filter(username=username)
    if me.username == username:
        my_follower = me.profile.followers.all()
        return Response({'followers': my_follower.count()}, status=200)

    if not other_user.exists():
         return Response({},status=404)
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
    return Response({'followers':current_follower.count()},status=200)