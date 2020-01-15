# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-10-31 03:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0324_sectionregulation_issue_due_date_window'),
    ]

    operations = [
        migrations.CreateModel(
            name='SanctionOutcomeDueDateConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date_window_1st', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('due_date_window_2nd', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('date_of_enforcement', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ('date_of_enforcement',),
                'verbose_name': 'CM_SanctionOutcomeDueDateConfiguration',
                'verbose_name_plural': 'CM_SanctionOutcomeDueDateConfiguration',
            },
        ),
    ]
