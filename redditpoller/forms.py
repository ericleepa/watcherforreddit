from django import forms

date_options = [('1', 'hourly'), ('24', 'daily'), ('168', 'weekly')]


class WatchThread(forms.Form):
    reddit_thread_url = forms.URLField(label='',
                                        max_length=500, widget=forms.TextInput(attrs={'placeholder':
                                       'e.g. https://www.reddit.com/r/learnpython/comments/5jgbiq/python_oop_series/'}))
    watch_interval = forms.ChoiceField(choices=date_options,
                                       label='Select the frequency of which you would like to be updated',
                                       widget=forms.RadioSelect())


class WatchSubreddit(forms.Form):
    subreddit_name = forms.CharField(label='',
                                        max_length=30, widget=forms.TextInput(attrs={'placeholder':
                                                                                     'e.g. learnpython'}))
    watch_interval = forms.ChoiceField(choices=date_options,
                                       label='Select the frequency of which you would like to be updated',
                                       widget=forms.RadioSelect())


class WatchUser(forms.Form):
    username = forms.CharField(label='', max_length=30, widget = forms.TextInput(attrs={'placeholder': 'e.g. wil'}))
    watch_interval = forms.ChoiceField(choices=date_options,
                                       label='Select the frequency of which you would like to be updated',
                                       widget=forms.RadioSelect())
