from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Q

class TweetQuerySet(models.QuerySet):

    def feed(self,user):
        profiles_exist = user.following.exists()
        print(profiles_exist)
        follow_user_id = []
        if profiles_exist:
            follow_user_id = user.following.values_list('user__id',flat=True)
        return self.filter(Q(user__id__in=follow_user_id) |
                                  Q(user=user)).distinct().order_by("-timestamp")

class TweetManager(models.Manager):

    def get_queryset(self,*args,**kwargs):
        return TweetQuerySet(self.model,using=self._db)

    def feed(self,user):
        return self.get_queryset().feed(user)


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

    objects = TweetManager()
    class Meta:
        ordering = ['-id']

    @property
    def is_retweet(self):
        return self.parent != None


class FollowerRelation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile',on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    location = models.CharField(max_length=220,null=True,blank=True)
    bio = models.TextField(blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    followers = models.ManyToManyField(User,related_name='following',blank=True)


    def user_did_save(sender,instance,created,*args,**kwargs):
        if created:
            Profile.objects.get_or_create(user=instance)

        post_save.connect(user_did_save,sender=User)

