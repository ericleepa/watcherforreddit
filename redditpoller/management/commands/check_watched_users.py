from django.core.management import BaseCommand
from django.utils import timezone
from redditpoller.models import WatchedUser, WatchedUserComment, WatchedUserThread
from redditpoller.poller import get_user_threads, get_user_comments, notify_user
from datetime import timedelta


class Command(BaseCommand):
    help = "Checks watched users and notifies users of updates"

    def handle(self, *args, **options):
        watched_users = WatchedUser.objects.all()
        user_count = watched_users.count()
        notifications_sent = 0
        for user in watched_users:
            current_time = timezone.now()
            if current_time - timedelta(hours=user.watch_interval) < user.last_checked_date:
                pass
            else:
                user.last_checked_date = current_time
                user.save()
                new_threads = get_user_threads(user.watched_username, 10)
                linked_threads = WatchedUserThread.objects.filter(parent_user=user)
                thread_list = []
                new_thread_count = 0
                for thread in new_threads:
                    if linked_threads.filter(url=thread.permalink).exists():
                        pass
                    else:
                        thread_list.append([thread.title, thread.permalink])
                        t = WatchedUserThread(parent_user=user, url=thread.permalink,
                                                   title=thread.title, thread_date=thread.created)
                        t.save()
                        new_thread_count += 1
                new_comments = get_user_comments(user.watched_username, 10)
                linked_comments = WatchedUserComment.objects.filter(parent_user=user)
                new_comment_count = 0
                comment_list = []
                for comment in new_comments:
                    if linked_comments.filter(url=comment.permalink(fast=True)).exists():
                        pass
                    else:
                        c = WatchedUserComment(parent_user=user, url=comment.permalink(fast=True),
                                                text=comment.body)
                        c.save()
                        comment_list.append([comment.body, comment.permalink(fast=True)])
                        new_comment_count += 1
                if new_comment_count == 0 and  new_thread_count == 0:
                    pass
                else:
                    formatted_comments = ''
                    # only grab 3 comments as to not reach character limit
                    limit_comments = 3
                    for comment in comment_list:
                        if limit_comments > 0:
                            formatted_comments += '\n\n' + comment[0] + ' - [Link](https://reddit.com{})'.format(
                                comment[1])
                            limit_comments -= 1
                        else:
                            break
                    formatted_thread_titles = ''
                    limit_threads = 3
                    for thr in thread_list:
                        if limit_threads > 0:
                            formatted_thread_titles += '\n\n' + thr[0] + ' - [Link](https://reddit.com{})'.format(
                                thr[1])
                            limit_threads -= 1
                        else:
                            break
                    all_formatted = formatted_thread_titles + formatted_comments
                    username = str(user.user)
                    notify_user(username,
                                '{} new comment(s) {} new thread(s) and by the user **"{}"** - view user [here]'
                                '(https://reddit.com/u/{}) \n\n *** \n *^preview* {} \n *** \n'
                                '^[[Information]](http://reddit.com/u/reddit_watcher) ^| '
                                '^[[Code]](https://github.com/ericleepa/watcherforreddit) ^| ^[[Contact]]'
                                '(https://www.reddit.com/message/compose/?to=ericleepa&subject=watcher)'
                                .format(new_comment_count, new_thread_count, user.watched_username,
                                        user.watched_username, all_formatted))
                    notifications_sent += 1
        return 'check_watched_users run. {} users checked and {} notifications sent' \
                .format(user_count, notifications_sent)