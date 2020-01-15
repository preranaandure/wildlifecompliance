# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-07-30 07:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0268_inspection_inform_party_being_inspected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='status',
            field=models.CharField(choices=[('open', 'Open'), ('endorsement', 'Awaiting Endorsement'), ('sanction_outcome', 'Awaiting Sanction Outcomes'), ('discarded', 'Discarded'), ('closed', 'Closed')], default='open', max_length=100),
        ),
    ]
