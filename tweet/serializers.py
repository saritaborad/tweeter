from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from tweet.models import Tweet,Comment
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


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['tweet', 'content', 'user', 'reply_parent']
        extra_kwargs = {'reply_parent': {'write_only': True}}


    def get_user(self, obj):
        return str(obj.user.username)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField(method_name="get_all_reply")

    class Meta:
        model = Comment
        fields = ['tweet','content','user','reply']


    def get_user(self,obj):
        return str(obj.user.username)

    def get_all_reply(self, obj):
        if obj.reply_parent is None:
            return Comment.objects.none()
        qs = Comment.objects.filter(reply_parent_id=obj.reply_parent.pk)
        serializer = ReplySerializer(qs, many=True)
        return serializer.data

class TweetSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField(read_only=True)
    comments = CommentSerializer(many=True)
    parent = TweetCreateSerializer(read_only=True)

    class Meta:
        model = Tweet
        fields = ['content', 'user', 'likes', 'is_retweet', 'parent', 'comments']

    def get_likes(self, obj):
        return obj.likes.count()

    def get_user(self, obj):
        return str(obj.user.username)

class TweetListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    tweet_detail = serializers.HyperlinkedIdentityField(view_name='detail', lookup_field='pk')

    class Meta:
        model = Tweet
        fields = ['content', 'user', 'tweet_detail']

    def get_user(self, obj):
        return str(obj.user.username)

class TweetActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    action = serializers.CharField()
    content = serializers.CharField(allow_blank=True, required=False)

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError('this is not a valid action')
        return value






































































































































































