# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-29 02:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0264_merge_20190726_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='callemail',
            name='date_of_call',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='callemail',
            name='time_of_call',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
