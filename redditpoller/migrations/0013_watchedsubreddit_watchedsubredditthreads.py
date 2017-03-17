# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-04 20:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('redditpoller', '0012_auto_20170304_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatchedSubreddit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('username', models.CharField(max_length=25)),
                ('checked_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='WatchedSubredditThreads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('thread_date', models.CharField(max_length=50)),
                ('parent_subreddt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='redditpoller.WatchedSubreddit')),
            ],
        ),
    ]
