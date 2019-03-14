# Generated by Django 2.1.8 on 2019-03-11 15:36

import actions.utils
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0008_auto_20190311_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='headers',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=actions.utils.SkipJSONEncoder),
        ),
        migrations.AlterField(
            model_name='action',
            name='payload',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]