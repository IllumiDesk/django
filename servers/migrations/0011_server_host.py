# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-13 11:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0001_initial'),
        ('servers', '0010_auto_20170404_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='servers', to='infrastructure.DockerHost'),
        ),
    ]