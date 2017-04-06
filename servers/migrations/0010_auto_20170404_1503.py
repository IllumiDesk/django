# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-04 15:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0009_auto_20170328_1258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='port',
        ),
        migrations.AlterField(
            model_name='server',
            name='connected',
            field=models.ManyToManyField(blank=True, related_name='_server_connected_+', to='servers.Server'),
        ),
    ]
