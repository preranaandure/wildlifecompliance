# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-01-22 06:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wildlifecompliance', '0396_briefofevidencerecordofinterviewtree'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='briefofevidencerecordofinterviewtree',
            name='legal_case',
        ),
        migrations.DeleteModel(
            name='BriefOfEvidenceRecordOfInterviewTree',
        ),
    ]
