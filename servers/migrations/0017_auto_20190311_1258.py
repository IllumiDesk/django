# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-03-11 12:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0016_auto_20180914_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servers', to='infrastructure.DockerHost'),
        ),
        migrations.AlterField(
            model_name='serverrunstatistics',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='serverrunstatistics',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.Project'),
        ),
        migrations.AlterField(
            model_name='serverrunstatistics',
            name='server',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='servers.Server'),
        ),
        migrations.AlterField(
            model_name='serverstatistics',
            name='server',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='servers.Server'),
        ),
    ]