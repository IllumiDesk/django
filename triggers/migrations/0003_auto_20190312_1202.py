# Generated by Django 2.1.8 on 2019-03-12 12:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import triggers.models


class Migration(migrations.Migration):

    dependencies = [
        ('triggers', '0002_auto_20190311_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='webhook',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=triggers.models.webhook_default),
        ),
    ]
