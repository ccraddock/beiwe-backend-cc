# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-01-15 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0021_auto_20190115_2244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participantsurvey',
            name='name',
            field=models.TextField(help_text='Name of the study; can be of any length', unique=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='name',
            field=models.TextField(help_text='Name of the study; can be of any length', unique=True),
        ),
        migrations.AlterField(
            model_name='surveyarchive',
            name='name',
            field=models.TextField(help_text='Name of the study; can be of any length', unique=True),
        ),
    ]
