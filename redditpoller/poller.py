import praw
import prawcore


r = praw.Reddit('bot1', user_agent='python script v0.5 (by /u/ericleepa)')


def get_reddit_thread(reddit_url):
    thread = r.submission(url=reddit_url)
    return thread


def get_reddit_comments_from_thread(thread):
    thread.comments.replace_more(limit=0)
    thread_comments = thread.comments.list()
    return thread_comments


def notify_user(redditor, message):
    r.redditor(redditor).message('Reddit Watcher', message)


def user_exists(user):
    try:
        r.redditor(user).fullname
    except prawcore.exceptions.NotFound:
        return False
    return True


def subreddit_exists(subreddit):
    try:
        r.subreddit(subreddit).fullname
    except prawcore.exceptions.Redirect:
        return False
    return True


def get_subreddit_threads(subreddit_name, fetch_amount):
    thread = r.subreddit(subreddit_name).new(limit=fetch_amount)
    return thread


def authorize_reddit_account(state):
    a = praw.Reddit('bot2', user_agent='django web authentication app v0.5 (by /u/ericleepa)')
    url = a.auth.url(['identity'], state, duration='temporary')
    return url


def reddit_code_to_username(code):
    a = praw.Reddit('bot2', user_agent='django web authentication app v0.5 (by /u/ericleepa)')
    a.auth.authorize(code)
    return a.user.me().name


def get_user_comments(username, fetch_amount):
    comments = r.redditor(username).comments.new(limit=fetch_amount)
    return comments


def get_user_threads(username, fetch_amount):
    threads = r.redditor(username).submissions.new(limit=fetch_amount)
    return threads
