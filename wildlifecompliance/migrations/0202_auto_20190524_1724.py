# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-05-24 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0201_auto_20190523_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionDistrict',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('SWAN', 'Swan Region'), ('PHD', 'Perth Hills'), ('SCD', 'Swan Coastal'), ('SWR', 'South West Region'), ('BWD', 'Blackwood'), ('WTN', 'Wellington'), ('WR', 'Warren Region'), ('DON', 'Donnelly'), ('FRK', 'Frankland'), ('SCR', 'South Coast Region'), ('ALB', 'Albany'), ('ESP', 'Esperance'), ('KIMB', 'Kimberley Region'), ('EKD', 'East Kimberley'), ('WKD', 'West Kimberley'), ('PIL', 'Pilbara Region'), ('EXM', 'Exmouth'), ('GLD', 'Goldfields Region'), ('MWR', 'Midwest Region'), ('GER', 'Geraldton'), ('KLB', 'Kalbarri'), ('MOR', 'Moora'), ('SHB', 'Shark Bay'), ('WBR', 'Wheatbelt Region'), ('CWB', 'Central Wheatbelt'), ('SWB', 'Southern Wheatbelt'), ('AV', 'Aviation'), ('OTH', 'Other')], default='OTH', max_length=32)),
            ],
        ),
        migrations.AlterModelOptions(
            name='compliancepermissiongroup',
            options={'verbose_name': 'CM_Compliance Permission group', 'verbose_name_plural': 'CM_Compliance permission groups'},
        ),
        migrations.AddField(
            model_name='compliancepermissiongroup',
            name='region_district',
            field=models.ManyToManyField(blank=True, to='wildlifecompliance.RegionDistrict'),
        ),
    ]
