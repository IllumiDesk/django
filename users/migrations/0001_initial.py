# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 17:34
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('address', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('public', models.BooleanField(default=False)),
                ('unsubscribed', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('integration_id', models.CharField(max_length=64)),
                ('integration_email', models.CharField(max_length=255)),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, size=None)),
                ('provider', models.CharField(max_length=255)),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('avatar_url', models.CharField(blank=True, max_length=100, null=True)),
                ('bio', models.CharField(blank=True, max_length=400, null=True)),
                ('url', models.CharField(blank=True, max_length=200, null=True)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=120, null=True)),
                ('company', models.CharField(blank=True, max_length=255, null=True)),
                ('current_login_ip', models.CharField(blank=True, max_length=20, null=True)),
                ('last_login_ip', models.CharField(blank=True, max_length=20, null=True)),
                ('login_count', models.IntegerField(blank=True, null=True)),
                ('timezone', models.CharField(blank=True, db_column='Timezone', max_length=20, null=True)),
                ('billing_address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.BillingAddress')),
                ('billing_plan', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='billing.BillingPlan')),
            ],
        ),
        migrations.AddField(
            model_name='integration',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='integrations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='email',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='emails', to=settings.AUTH_USER_MODEL),
        ),
    ]
