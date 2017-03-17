from django.core.management import BaseCommand
from django.utils import timezone
from redditpoller.models import WatchedThread, WatchedComment
from redditpoller.poller import get_reddit_thread, get_reddit_comments_from_thread, notify_user
from datetime import timedelta


class Command(BaseCommand):
    help = "Checks watched threads and notifies users of updates"

    def handle(self, *args, **options):
        watched_threads = WatchedThread.objects.all()
        thread_count = watched_threads.count()
        notifications_sent = 0
        for thread in watched_threads:
            current_time = timezone.now()
            if current_time - timedelta(hours=thread.watch_interval) < thread.last_checked_date:
                pass
            else:
                thread.last_checked_date = current_time
                thread.save()
                praw_thread = get_reddit_thread('https://reddit.com' + thread.url)
                username = thread.user.username
                if thread.archived != praw_thread['thread_archived']:
                    notify_user(username, 'The thread {} has been archived'
                                          'If you would like to watch another thread go [here.]'
                                          '(http://www.reddit.com'.format(thread.title))
                    thread.delete()
                    break
                if thread.self_text != praw_thread['thread_self_text']:
                    notify_user(username, 'The author of thread "{}" has changed the submission text.'
                                          ' You can view the post [here](https://reddit.com/{})'
                                .format(thread.title, thread.url))
                    thread.delete()
                    break
                if praw_thread.num_comments > 500:
                    notify_user(username, 'The thread {} has reached 500 comments'
                                          ' and will no longer be watched.  This tool is only designed to watch small'
                                          ' threads. If you would like to watch another thread go [here.]'
                                          '(http://www.reddit.com)'.format(thread.title))
                    thread.delete()
                    break
                linked_comments = WatchedComment.objects.filter(parent_thread=thread)
                new_comments = get_reddit_comments_from_thread(praw_thread['thread'])
                new_comment_count = 0
                comment_list = []
                for comment in new_comments:
                    if linked_comments.filter(url=comment['comment_permalink']).exists():
                        pass
                    else:
                        c = WatchedComment(parent_thread=thread, url=comment['comment_permalink'],
                                           text=comment['comment_body'])
                        c.save()
                        comment_list.append([comment['comment_body'], comment['comment_permalink']])
                        new_comment_count += 1
                if new_comment_count == 0:
                    pass
                else:
                    formatted_comments = ''
                    # only grab 5 comments as to not reach character limit
                    limit_comments = 5
                    for comment in comment_list:
                        if limit_comments > 0:
                            formatted_comments += '\n\n' + comment[0] + ' - [Link](https://reddit.com{})'.format(comment[1])
                            limit_comments -= 1
                        else:
                            break
                    notify_user(username, '{} new comment(s) in the thread **"{}"** - view thread [here.]'
                                          '(https://reddit.com/{})  \n\n *** \n *^comment ^preview* {} \n\n *** \n'
                                          '^[[Information]](http://reddit.com/u/reddit_watcher) ^| '
                                          '^[[Code]](https://github.com/ericleepa/watcherforreddit) ^| ^[[Contact]]'
                                          '(https://www.reddit.com/message/compose/?to=ericleepa&subject=watcher)'
                                .format(new_comment_count, thread.title, thread.url, formatted_comments))
                    notifications_sent += 1
        return 'check_watched_threads run. {} threads checked and {} notifications sent'\
            .format(thread_count, notifications_sent)
