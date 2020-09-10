from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from tweet.models import Tweet, Comment
from rest_framework import serializers

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = ['like', 'unlike', 'retweet']


class TweetCreateSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tweet
        fields = ['content', 'user', 'likes']

    def get_likes(self, obj):
        return obj.likes.count()

    def get_user(self, obj):
        return str(obj.user.username)

    def validate_content(self, value):
        if len('content') > MAX_TWEET_LENGTH:
            raise serializers.ValidationError('This is too long ')
        return value



class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['tweet','reply_parent', 'content', 'user']
        # extra_kwargs = {'comment':{'write_only':True}}

    def get_user(self, obj):
        return str(obj.user.username)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    # replies = ReplySerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField(method_name="get_all_reply")
    # comments = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['tweet', 'content', 'user', 'replies']

    def get_user(self, obj):
        return str(obj.user.username)

    def get_all_reply(self, obj):
        if obj.reply_parent_id is None:
            comment_id = obj.id
            reply_obj = Comment.objects.filter(reply_parent_id=comment_id)
            if reply_obj.exists():
                serializer = ReplySerializer(reply_obj, many=True)
                # print(serializer.data)
                return serializer.data
            return Comment.objects.none()


class TweetSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)

    # parent = TweetCreateSerializer(read_only=True)

    class Meta:
        model = Tweet
        fields = ['content', 'user', 'likes', 'is_retweet', 'comments']
        # extra_kwargs = {'parent':{'write_only':True}}

    def get_likes(self, obj):
        return obj.likes.count()

    def get_user(self, obj):
        return str(obj.user.username)

    def get_comments(self,obj):
        comment_qs = obj.comments.all()
        for comment in comment_qs:
            if comment.reply_parent_id is None:
                serializer = CommentSerializer(comment)
                return serializer.data



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
