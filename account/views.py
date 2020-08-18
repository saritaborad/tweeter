from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
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
from account.serializers import *
from django.db.models import Q


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
            return Response(new_data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class PasswrodResetAPIView(generics.GenericAPIView):
    serializer_class = PasswrodResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hi ' + user.username + '\n Use link below to reset your password\n' + absurl
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'reset your password'}
            SendMail.send_mail(data)
        return Response({'success': 'we have sent you link to reset password'})

class PasswordTokenCheckAPIView(generics.GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is invalid, please generate new'}, status=401)
            return Response({'success': True, 'message': 'credential valid', 'uidb64': uidb64, 'token': token},
                            status=200)
        except DjangoUnicodeDecodeError as identifier:
            print(identifier)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        return Response({'success': True, 'message': 'Password reset success'}, status=200)

