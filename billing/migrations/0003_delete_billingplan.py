# -*- coding: utf-8 -*-
# Generated by Django 1.11.2.dev20170516103530 on 2017-05-17 13:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170517_1330'),
        ('billing', '0002_auto_20170517_1330'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BillingPlan',
        ),
    ]
