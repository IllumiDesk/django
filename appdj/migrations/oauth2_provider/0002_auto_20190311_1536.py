# Generated by Django 2.1.8 on 2019-03-11 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2_provider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='source_refresh_token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refreshed_access_token', to=settings.OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL),
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='application',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='application',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='grant',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='grant',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='revoked',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='refreshtoken',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL),
        ),
        migrations.AlterField(
            model_name='accesstoken',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_accesstoken', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='application',
            name='redirect_uris',
            field=models.TextField(blank=True, help_text='Allowed URIs list, space separated'),
        ),
        migrations.AlterField(
            model_name='grant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_grant', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='refreshtoken',
            name='access_token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refresh_token', to=settings.OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL),
        ),
        migrations.AlterField(
            model_name='refreshtoken',
            name='token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='refreshtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='oauth2_provider_refreshtoken', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='refreshtoken',
            unique_together={('token', 'revoked')},
        ),
    ]
