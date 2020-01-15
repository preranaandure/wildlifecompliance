# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-17 02:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0255_inspection_inspection_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('endorsement', 'Awaiting Endorsement'), ('sanction_outcome', 'Awaiting Sanction Outcomes'), ('closed', 'Closed')], default='open', max_length=100),
        ),
    ]
