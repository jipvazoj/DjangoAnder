# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-16 22:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_ranking'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ranking',
            name='id',
        ),
        migrations.AlterField(
            model_name='ranking',
            name='nombre',
            field=models.CharField(max_length=200, primary_key=True, serialize=False),
        ),
    ]