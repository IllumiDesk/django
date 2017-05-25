# -*- coding: utf-8 -*-
# Generated by Django 1.11.2.dev20170524113944 on 2017-05-24 15:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0012_invoiceitem_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='application_fee',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='attempt_count',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
