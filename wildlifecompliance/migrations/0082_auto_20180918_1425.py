# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-09-18 06:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0081_remove_applicationgrouptype_display_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationgrouptype',
            old_name='name',
            new_name='type',
        ),
        migrations.AddField(
            model_name='applicationgrouptype',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Group Name'),
        ),
    ]
