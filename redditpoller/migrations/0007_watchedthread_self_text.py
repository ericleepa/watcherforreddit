# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 15:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('redditpoller', '0006_auto_20170228_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchedthread',
            name='self_text',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
