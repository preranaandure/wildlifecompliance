# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-04-08 08:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0158_auto_20190408_1540'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Referrers',
            new_name='Referrer',
        ),
    ]
