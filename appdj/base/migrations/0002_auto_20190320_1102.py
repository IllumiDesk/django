# Generated by Django 2.1.8 on 2019-03-20 11:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("DROP TABLE IF EXISTS triggers_trigger"),
        migrations.RunSQL("DROP TABLE IF EXISTS actions_action"),
    ]
