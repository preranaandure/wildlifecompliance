# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-06-14 11:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0615_auto_20220614_1623'),
    ]

    operations = [
        migrations.RenameField(
            model_name='compliancemanagementsystemgrouppermission',
            old_name='compliance_management_system_group',
            new_name='group',
        ),
    ]