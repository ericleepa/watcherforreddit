from django.contrib import admin
from .models import (WatchedThread, WatchedComment, WatchedSubreddit,
    WatchedSubredditThread, WatchedUser, WatchedUserComment, WatchedUserThread)


admin.site.register(WatchedThread)
admin.site.register(WatchedComment)
admin.site.register(WatchedSubreddit)
admin.site.register(WatchedSubredditThread)
admin.site.register(WatchedUser)
admin.site.register(WatchedUserComment)
admin.site.register(WatchedUserThread)