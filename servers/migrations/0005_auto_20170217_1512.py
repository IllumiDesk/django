# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 15:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0004_auto_20170217_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='server',
        ),
        migrations.RemoveField(
            model_name='model',
            name='server',
        ),
        migrations.DeleteModel(
            name='Job',
        ),
        migrations.DeleteModel(
            name='Model',
        ),
    ]