from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class WatchedThread(models.Model):
    user = models.ForeignKey(User)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    thread_date = models.CharField(max_length=50)
    archived = models.BooleanField(default=False)
    self_post = models.BooleanField(default=False)
    self_text = models.CharField(max_length=10000, null=True, blank=True)
    submitted_date = models.DateTimeField(default=timezone.now)
    last_checked_date = models.DateTimeField(default=timezone.now)
    watch_interval = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title


class WatchedComment(models.Model):
    parent_thread = models.ForeignKey(WatchedThread, on_delete=models.CASCADE)
    comment_author = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(max_length=500)
    text = models.CharField(max_length=10000)

    def __str__(self):
        return self.url


class WatchedSubreddit(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=30)
    submitted_date = models.DateTimeField(default=timezone.now)
    last_checked_date = models.DateTimeField(default=timezone.now)
    watch_interval = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class WatchedSubredditThread(models.Model):
    parent_subreddit = models.ForeignKey(WatchedSubreddit, on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    thread_date = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class WatchedUser(models.Model):
    user = models.ForeignKey(User)
    watched_username = models.CharField(max_length=30)
    submitted_date = models.DateTimeField(default=timezone.now)
    last_checked_date = models.DateTimeField(default=timezone.now)
    watch_interval = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.watched_username


class WatchedUserComment(models.Model):
    parent_user = models.ForeignKey(WatchedUser, on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    text = models.CharField(max_length=10000)

    def __str__(self):
        return self.url


class WatchedUserThread(models.Model):
    parent_user = models.ForeignKey(WatchedUser, on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    title = models.CharField(max_length=500)
    thread_date = models.CharField(max_length=50)

    def __str__(self):
        return self.title
