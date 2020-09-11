from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TweetLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey("Tweet", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Tweet(models.Model):
    parent = models.ForeignKey('self',null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(User,related_name='tweet_user',blank=True,through=TweetLike)
    image = models.FileField(upload_to='images/',blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.content[:30] + '  ....'

    @property
    def is_retweet(self):
        return self.parent != None

class Comment(models.Model):
    tweet = models.ForeignKey(Tweet,on_delete=models.CASCADE,
                              related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reply_parent = models.ForeignKey('self',null=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)


    def __str__(self):
        return f'Comment by {self.user.username} on {self.tweet}'



# class Reply(models.Model):
#     comment = models.ForeignKey(Comment,on_delete=models.CASCADE,
#                               related_name='replies')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)

class FollowerRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=220, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def __str__(self):
        return self.user.username

    @receiver(post_save,sender=User)
    def user_did_save(sender, instance, created, *args, **kwargs):
        if created:
            Profile.objects.get_or_create(user=instance)
        else:
            instance.profile.save()
