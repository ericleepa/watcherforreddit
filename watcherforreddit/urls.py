"""redditthreadwatcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from redditpoller import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^homepage/', views.home_page, name='home'),
    url(r'^callback/', views.callback, name='callback'),
    url(r'^signin/', views.redirect_to_reddit_auth, name='redditauth'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^about/', views.about, name='about'),
    url(r'^mywatched/', views.get_watched_items, name='mywatched'),
    url(r'^watchthread/', views.watch_thread, name='watchthread'),
    url(r'^watchuser/', views.watch_user, name='watchuser'),
    url(r'^watchsubreddit/', views.watch_subreddit, name='watchsubreddit'),
    url(r'^watchedthread/', views.watched_thread, name='watchedthread'),
    url(r'^watchedsubreddit/', views.watched_subreddit, name='watchedsubreddit'),
    url(r'^watcheduser/', views.watched_user, name='watcedhuser'),
    url(r'^forceupdate/', views.check_watched_page, name='forceupdate'),
    url(r'^forcecheckthreads/', views.check_watched_threads, name='forcecheckthreads'),
    url(r'^forcecheckusers/', views.check_watched_users, name='forcecheckusers'),
    url(r'^forcechecksubreddits/', views.check_watched_subreddits, name='forcechecksubreddits'),
    url(r'^deletethread/(?P<pk>\d+)/$', views.delete_thread, name='deletethread'),
    url(r'^deletesubreddit/(?P<pk>\d+)/$', views.delete_subreddit, name='deletesubreddit'),
    url(r'^deleteuser/(?P<pk>\d+)/$', views.delete_user, name='deleteuser'),
]
