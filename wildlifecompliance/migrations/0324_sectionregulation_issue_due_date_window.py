# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-10-31 03:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0323_auto_20191029_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='sectionregulation',
            name='issue_due_date_window',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
