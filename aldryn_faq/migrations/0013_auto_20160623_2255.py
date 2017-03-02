# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-24 02:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_faq', '0012_categorytranslation_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='latestquestionsplugin',
            name='cache_duration',
            field=models.PositiveSmallIntegerField(default=0, help_text="The maximum duration (in seconds) that this plugin's content should be cached."),
        ),
        migrations.AddField(
            model_name='mostreadquestionsplugin',
            name='cache_duration',
            field=models.PositiveSmallIntegerField(default=0, help_text="The maximum duration (in seconds) that this plugin's content should be cached."),
        ),
        migrations.AddField(
            model_name='topquestionsplugin',
            name='cache_duration',
            field=models.PositiveSmallIntegerField(default=0, help_text="The maximum duration (in seconds) that this plugin's content should be cached."),
        ),
    ]