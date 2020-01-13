# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2019-08-14 06:14
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wildlifecompliance', '0279_remove_callemail_inspection_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SanctionOutcomeUserAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('what', models.TextField()),
            ],
            options={
                'ordering': ('-when',),
            },
        ),
        migrations.AlterField(
            model_name='sanctionoutcome',
            name='status',
            field=models.CharField(choices=[(b'draft', b'Draft'), (b'with_manager', b'With Mnager'), (b'with_officer', b'With Officer'), (b'closed', b'Closed'), (b'withdrawn', b'Withdrawn'), (b'closed_issued', b'Closed (Issued)'), (b'closed_withdrawn', b'Closed (Withdrawn)'), (b'awaiting_payment', b'Awaiting Payment'), (b'awaiting_payment_extended', b'Awaiting Payment Extended)'), (b'issued', b'Issued'), (b'overdue', b'Overdue')], default=b'draft', max_length=40),
        ),
        migrations.AddField(
            model_name='sanctionoutcomeuseraction',
            name='sanction_outcome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_logs', to='wildlifecompliance.SanctionOutcome'),
        ),
        migrations.AddField(
            model_name='sanctionoutcomeuseraction',
            name='who',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
