# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-10-21 15:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myaddr', '0001_initial'),
        ('user', '0002_user_email_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='myaddr.Address', verbose_name='默认地址'),
        ),
    ]