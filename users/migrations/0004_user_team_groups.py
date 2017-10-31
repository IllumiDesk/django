# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-10-18 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
        ('users', '0003_auto_20170803_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='team_groups',
            field=models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='teams.Group'),
        ),
    ]
