# -*- coding: utf-8 -*-
# Generated by Django 1.11.2.dev20170519134547 on 2017-05-19 14:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170519_1419'),
        ('billing', '0002_auto_20170519_1419')
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='billing_plan',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.Plan'),
        ),
    ]