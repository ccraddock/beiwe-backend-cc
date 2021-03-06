# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-12 01:44
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0013_auto_20180530_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantAliases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('reference_id', models.CharField(help_text=b'Eight-character unique ID with characters chosen from 1-9 and a-z', max_length=8, unique=True, validators=[django.core.validators.RegexValidator(b'^[1-9a-z]+$', message=b'This field can only contain characters 1-9 and a-z.')])),
                ('alias_id', models.CharField(help_text=b'Eight-character unique ID with characters chosen from 1-9 and a-z', max_length=8, unique=True, validators=[django.core.validators.RegexValidator(b'^[1-9a-z]+$', message=b'This field can only contain characters 1-9 and a-z.')])),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='participant_aliases', to='database.Study')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
