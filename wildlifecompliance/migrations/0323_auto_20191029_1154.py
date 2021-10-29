# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-10-29 03:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0322_auto_20191025_1122'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='penaltyamount',
            options={'ordering': ('date_of_enforcement',), 'verbose_name': 'CM_PenaltyAmount', 'verbose_name_plural': 'CM_PenaltyAmounts'},
        ),
        migrations.RemoveField(
            model_name='penaltyamount',
            name='time_of_enforcement',
        ),
        migrations.AddField(
            model_name='penaltyamount',
            name='amount_after_due',
            field=models.DecimalField(decimal_places=2, default=str(b'0.00', 'utf-8'), max_digits=8),
        ),
    ]
