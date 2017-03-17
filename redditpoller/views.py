from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from redditpoller.forms import WatchThread, WatchSubreddit, WatchUser
from redditpoller.poller import get_reddit_thread, get_reddit_comments_from_thread, user_exists, subreddit_exists, \
    get_subreddit_threads, get_user_comments, get_user_threads, authorize_reddit_account, reddit_code_to_username
from redditpoller.models import WatchedThread, WatchedComment, WatchedSubreddit, WatchedSubredditThread, WatchedUser, \
    WatchedUserComment, WatchedUserThread


def home_page(request):
    return render(request, 'homepage.html')


def about(request):
    return render(request, 'about.html')


def redirect_to_reddit_auth(request):
    from uuid import uuid4
    reddit_state = str(uuid4())
    request.session['reddit_state'] = reddit_state
    auth_url = authorize_reddit_account(reddit_state)
    print(request.session['reddit_state'])
    return redirect(auth_url)


def callback(request):
    if request.method == 'GET':
        if request.session['reddit_state'] == request.GET.get('state'):
            code = request.GET.get('code')
            reddit_username = reddit_code_to_username(code)
            if User.objects.filter(username=reddit_username).exists():
                user = authenticate(username=reddit_username)
                login(request, user)
                return redirect('/')
            else:
                User.objects.create_user(username=reddit_username)
                user = authenticate(username=reddit_username)
                login(request, user)
            return redirect('/')
        else:
            return render(request, 'error.html', {'error': 'invalid request'})
    else:
        return render(request, 'error.html', {'error': 'You need to authorize your reddit account to use this site'})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/homepage/")


@login_required(login_url='/homepage/', redirect_field_name=None)
def index(request):
    return render(request, 'index.html')


@login_required(login_url='/homepage/', redirect_field_name=None)
def watch_thread(request):
    form = WatchThread(initial={'watch_interval': '1'})
    return render(request, 'watchthread.html', {'form': form})


@login_required(login_url='/homepage/', redirect_field_name=None)
def watch_subreddit(request):
    form = WatchSubreddit(initial={'watch_interval': '1'})
    return render(request, 'watchsubreddit.html', {'form': form})


@login_required(login_url='/homepage/', redirect_field_name=None)
def watch_user(request):
    form = WatchUser(initial={'watch_interval': '1'})
    return render(request, 'watchuser.html', {'form': form})


@login_required(login_url='/homepage/', redirect_field_name=None)
def watched_thread(request):
    if request.method == 'POST':
        form = WatchThread(request.POST)
        if form.is_valid():
            reddit_url = form.cleaned_data['reddit_thread_url']
            watch_interval = form.cleaned_data['watch_interval']
            try:
                if WatchedThread.objects.filter(user=request.user).count() > 9:
                    return render(request, 'error.html', {'error': 'Each account can only have up to ten watched '
                                                                   'threads'})
                praw_thread = get_reddit_thread(reddit_url)
                if WatchedThread.objects.filter(user=request.user, url=praw_thread.permalink).exists():
                    return render(request, 'error.html', {'error': 'You are already watching this thread'})
                if praw_thread.num_comments > 500:
                    return render(request, 'error.html', {'error': 'This tool can only track threads with less'
                                                                   ' than 500 comments'})
                elif praw_thread.archived:
                        return render(request, 'error.html', {'error': 'This thread is archived. There will be'
                                                              'no more changes to an archived thread'})
                else:
                    current_time = timezone.now()
                    t = WatchedThread(user=request.user, url=praw_thread.permalink,
                                      title=praw_thread.title, thread_date=praw_thread.created,
                                      archived=praw_thread.archived, self_post=praw_thread.is_self,
                                      self_text=praw_thread.selftext, submitted_date=current_time,
                                      last_checked_date=current_time, watch_interval=watch_interval)
                    t.save()
                    comments_list = get_reddit_comments_from_thread(praw_thread)
                    for comment in comments_list:
                        c = WatchedComment(parent_thread=t, url=comment.permalink(),
                                           text=comment.body)
                        c.save()
                    success_text = 'Thanks! You will be notified the next time there is an update to the thread:' \
                                   '  "{}"'.format(praw_thread.title)
                    return render(request, 'watched.html', {'success_text': success_text})
            except Exception as e:
                return render(request, 'error.html', {'error': e})


@user_passes_test(lambda u: u.is_superuser)
def check_watched_threads(request):
    run = call_command('check_watched_threads')
    return HttpResponse(run)


@login_required(login_url='/homepage/', redirect_field_name=None)
def watched_subreddit(request):
    if request.method == 'POST':
        form = WatchSubreddit(request.POST)
        if form.is_valid():
            subreddit_name = form.cleaned_data['subreddit_name']
            watch_interval = form.cleaned_data['watch_interval']
            try:
                if WatchedSubreddit.objects.filter(user=request.user).count() > 9:
                    return render(request, 'error.html', {'error': 'Each account can only have up to ten watched '
                                                                   'subreddits'})
                if WatchedSubreddit.objects.filter(user=request.user, name=subreddit_name).exists():
                    return render(request, 'error.html', {'error': 'You are already watching this subreddit'})
                if subreddit_exists(subreddit_name):
                    current_time = timezone.now()
                    s = WatchedSubreddit(name=subreddit_name, user=request.user, submitted_date=current_time,
                                         last_checked_date=current_time, watch_interval=watch_interval)
                    s.save()
                    subreddit_threads_list = get_subreddit_threads(subreddit_name=subreddit_name, fetch_amount=100)
                    for thread in subreddit_threads_list:
                        t = WatchedSubredditThread(parent_subreddit=s, url=thread.permalink,
                                                   title=thread.title, thread_date=thread.created)
                        t.save()
                    success_text = 'Thanks! You will be notified the next time there is an update to the subreddit:' \
                                   '  "{}"'.format(subreddit_name)
                    return render(request, 'watched.html', {'success_text': success_text})
                else:
                    return render(request, 'error.html', {'error': 'This subreddit does not exist'})
            except Exception as e:
                return render(request, 'error.html', {'error': e})


@user_passes_test(lambda u: u.is_superuser)
def check_watched_subreddits(request):
    run = call_command('check_watched_subreddits')
    return HttpResponse(run)


@login_required(login_url='/homepage/', redirect_field_name=None)
def watched_user(request):
        form = WatchUser(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            watch_interval = form.cleaned_data['watch_interval']
            try:
                if WatchedUser.objects.filter(user=request.user).count() > 4:
                    return render(request, 'error.html', {'error': 'Each account can only have up to five watched '
                                                                   'users'})
                if WatchedUser.objects.filter(user=request.user, watched_username=username).exists():
                    return render(request, 'error.html', {'error': 'You are already watching this user'})
                if user_exists(username):
                    current_time = timezone.now()
                    u = WatchedUser(watched_username=username, user=request.user, submitted_date=current_time,
                                    last_checked_date=current_time, watch_interval=watch_interval)
                    u.save()
                    comments = get_user_comments(username, 20)
                    for comment in comments:
                        c = WatchedUserComment(parent_user=u, url=comment.permalink(fast=True), text=comment.body)
                        c.save()
                    threads = get_user_threads(username, 20)
                    for thread in threads:
                        t = WatchedUserThread(parent_user=u, url=thread.permalink, title=thread.title,
                                              thread_date=thread.created)
                        t.save()
                    success_text = 'Thanks! You will be notified the next time {} posts or comments:' \
                                   ''.format(username)
                    return render(request, 'watched.html', {'success_text': success_text})
                else:
                    return render(request, 'error.html', {'error': 'This user does not exist'})
            except Exception as e:
                return render(request, 'error.html', {'error': e})


@user_passes_test(lambda u: u.is_superuser)
def check_watched_users(request):
    run = call_command('check_watched_users')
    return HttpResponse(run)


@login_required(login_url='/homepage/', redirect_field_name=None)
def get_watched_items(request):
    thread_list = WatchedThread.objects.filter(user=request.user)
    subreddit_list = WatchedSubreddit.objects.filter(user=request.user)
    user_list = WatchedUser.objects.filter(user=request.user)
    return render(request, 'mywatched.html', {'thread_list': thread_list, 'subreddit_list': subreddit_list,
                                              'user_list': user_list})


@login_required(login_url='/homepage/', redirect_field_name=None)
def delete_thread(request, pk):
    thread_to_delete = WatchedThread.objects.get(pk=pk)
    if thread_to_delete.user == request.user:
        thread_to_delete.delete()
        return redirect(get_watched_items)
    else:
        return HttpResponse('Unauthorized', status=401)


@login_required(login_url='/homepage/', redirect_field_name=None)
def delete_subreddit(request, pk):
    subreddit_to_delete = WatchedSubreddit.objects.get(pk=pk)
    if subreddit_to_delete.user == request.user:
        subreddit_to_delete.delete()
        return redirect(get_watched_items)
    else:
        return HttpResponse('Unauthorized', status=401)


@login_required(login_url='/homepage/', redirect_field_name=None)
def delete_user(request, pk):
    user_to_delete = WatchedUser.objects.get(pk=pk)
    if user_to_delete.user == request.user:
        user_to_delete.delete()
        return redirect(get_watched_items)
    else:
        return HttpResponse('Unauthorized', status=401)


@user_passes_test(lambda u: u.is_superuser)
def check_watched_page(request):
    return render(request, 'forceupdate.html')
