from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Tweet

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode

from rest_framework import serializers


MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = ['like','unlike','retweet']


class TweetCreateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tweet
        fields = ['content','user','likes']

    def get_likes(self,obj):
        return obj.likes.count()

    def get_user(self,obj):
        return str(obj.user.username)

    def validate_content(self,value):
        if len('content') > MAX_TWEET_LENGTH:
            raise serializers.ValidationError('This is too long ')
        return value

class TweetSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField(read_only=True)
    parent = TweetCreateSerializer(read_only =True)

    class Meta:
        model = Tweet
        fields = ['content','user','likes','is_retweet','parent']

    def get_likes(self,obj):
        return obj.likes.count()

    def get_user(self,obj):
        return str(obj.user.username)

class TweetListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    tweet_detail = serializers.HyperlinkedIdentityField(view_name='detail',lookup_field='pk')
    class Meta:
        model = Tweet
        fields = ['content','user','tweet_detail']

    def get_user(self,obj):
        return str(obj.user.username)

class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    content = serializers.CharField(allow_blank=True,required=False)

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError('this is not a valid action')
        return value




class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label='Email Address')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data['email']
        user_qs = User.objects.filter(email=email).exists()
        if user_qs:
            raise serializers.ValidationError('This user has already registered')
        return data

    def create(self, validated_data):
        print(validated_data)
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_obj = User(username=username, email=email)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(label='Email Address', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        user_obj = None
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        user = User.objects.filter(Q(email=email) & Q(username=username)).distinct()
        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise serializers.ValidationError('Username or Email is invalid.')
        if user_obj:
            if not user_obj.check_password(password):
                raise serializers.ValidationError('password is incorrect')

        return data


class PasswrodResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, data):
        try:
            password = data.get('passwrod ')
            token = data.get('token')
            uidb64 = data.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The reset link is invalid', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError('the reset link is invalid', 401)
        return super().validate(data)
