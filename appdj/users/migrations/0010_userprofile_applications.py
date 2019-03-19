# Generated by Django 2.1.8 on 2019-03-19 14:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ('users', '0009_auto_20190315_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='applications',
            field=models.ManyToManyField(related_name='users', to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ),
    ]
