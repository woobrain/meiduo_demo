# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-10-29 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oauthqquser',
            name='weibotoken',
            field=models.CharField(db_index=True, default=0, max_length=64, verbose_name='weibotoken'),
        ),
    ]