# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-27 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_form_partner'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='mostPlayed',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]
