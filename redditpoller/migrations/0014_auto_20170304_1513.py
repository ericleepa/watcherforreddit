# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-04 20:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('redditpoller', '0013_watchedsubreddit_watchedsubredditthreads'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watchedsubredditthreads',
            old_name='parent_subreddt',
            new_name='parent_subreddit',
        ),
    ]
