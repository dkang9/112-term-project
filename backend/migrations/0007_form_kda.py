# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-28 18:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_form_winrate'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='kda',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]