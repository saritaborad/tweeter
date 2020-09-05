from django.contrib import admin
from tweet.models import Tweet, TweetLike, Comment, Reply
from tweet.models import Profile


class TweetLikeAdmin(admin.TabularInline):
    model = TweetLike


class TweetAdmin(admin.ModelAdmin):
    inlines = [TweetLikeAdmin]
    list_display = ['__str__','user','id']
    search_fields = ['content','user__username']

    class Meta:
        model =Tweet

class CommentAdmin(admin.ModelAdmin):
    list_display = ['content','user','id']

    class Meta:
        model = Comment


class ReplyAdmin(admin.ModelAdmin):
    list_display = ['content', 'user']

    class Meta:
        model = Reply


admin.site.register(Tweet,TweetAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Reply,ReplyAdmin)
admin.site.register(Profile)