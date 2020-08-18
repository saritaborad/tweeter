from django.contrib import admin
from tweet.models import Tweet, TweetLike, Comment
from tweet.models import Profile


class TweetLikeAdmin(admin.TabularInline):
    model = TweetLike


class TweetAdmin(admin.ModelAdmin):
    inlines = [TweetLikeAdmin]
    list_display = ['__str__','user']
    search_fields = ['content','user__username']

    class Meta:
        model =Tweet


admin.site.register(Tweet,TweetAdmin)
admin.site.register(Comment)
admin.site.register(Profile)