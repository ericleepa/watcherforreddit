from django.core.management import BaseCommand
from django.utils import timezone
from redditpoller.models import WatchedSubreddit, WatchedSubredditThread
from redditpoller.poller import get_subreddit_threads, notify_user
from datetime import timedelta

class Command(BaseCommand):
    help = "Checks watched subreddits and notifies users of updates"

    def handle(self, *args, **options):
        watched_subreddits = WatchedSubreddit.objects.all()
        subreddit_count = watched_subreddits.count()
        notifications_sent = 0
        for subreddit in watched_subreddits:
            current_time = timezone.now()
            if current_time - timedelta(hours=subreddit.watch_interval) < subreddit.last_checked_date:
                pass
            else:
                subreddit.last_checked_date = current_time
                subreddit.save()
                new_threads = get_subreddit_threads(subreddit_name=subreddit.name, fetch_amount=50)
                linked_threads = WatchedSubredditThread.objects.filter(parent_subreddit=subreddit)
                # keep db from growing, only need the newest 100 submissions as a comparison
                if linked_threads.count() > 200:
                    # This works, but probably can be broken up into its own "cleanup function"
                    number_to_delete = abs(100 - linked_threads.count())
                    purge = linked_threads.order_by('thread_date')[:number_to_delete].values_list("id", flat=True)
                    WatchedSubredditThread.objects.filter(pk__in=list(purge)).delete()
                thread_list = []
                new_thread_count = 0
                for sthread in new_threads:
                    if linked_threads.filter(url=sthread.permalink).exists():
                        pass
                    else:
                        thread_list.append([sthread.title, sthread.permalink])
                        t = WatchedSubredditThread(parent_subreddit=subreddit, url=sthread.permalink,
                                                   title=sthread.title, thread_date=sthread.created)
                        t.save()
                        new_thread_count += 1

                if new_thread_count == 0:
                    pass
                else:
                    formatted_thread_titles = ''
                    limit_threads = 5
                    for thr in thread_list:
                        if limit_threads > 0:
                            formatted_thread_titles += '\n\n' + thr[0] + ' - [Link](https://reddit.com{})'.format(thr[1])
                            limit_threads -= 1
                        else:
                            break
                    username = subreddit.user.username
                    notify_user(username, '{} new thread(s) in the subreddit **"{}"** - view subreddit [here.]'
                                          '(https://reddit.com/r/{})  \n\n *** \n *^subreddit ^preview* {} \n *** \n'
                                          '^[[Information]](http://reddit.com/u/reddit_watcher) ^| '
                                          '^[[Code]](https://github.com/ericleepa/watcherforreddit) ^| ^[[Contact]]'
                                          '(https://www.reddit.com/message/compose/?to=ericleepa&subject=watcher)'
                                .format(new_thread_count, subreddit.name,
                                        subreddit.name, formatted_thread_titles))
                    notifications_sent += 1
        return 'check_watched_subreddits run. {} threads checked and {} notifications sent'\
            .format(subreddit_count, notifications_sent)
