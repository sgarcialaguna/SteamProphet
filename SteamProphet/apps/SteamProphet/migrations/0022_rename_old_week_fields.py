# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-24 18:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('SteamProphet', '0021_week'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='week',
            new_name='week_old',
        ),
        migrations.RenameField(
            model_name='votingperiod',
            old_name='week',
            new_name='week_old',
        ),
    ]
