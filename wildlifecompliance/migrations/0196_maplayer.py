# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-21 02:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0195_auto_20190510_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapLayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=100, null=True)),
                ('layer_name', models.CharField(blank=True, max_length=200, null=True)),
                ('availability', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'CM_MapLayer',
                'verbose_name_plural': 'CM_MapLayers',
            },
        ),
    ]
