# Generated by Django 2.1.8 on 2019-03-15 10:16

from django.conf import settings
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0016_auto_20180914_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='server',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='server',
            name='env_vars',
            field=django.contrib.postgres.fields.hstore.HStoreField(default=dict),
        ),
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