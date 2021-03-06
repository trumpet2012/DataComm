# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-25 00:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(default=uuid.uuid4)),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='networking.Session'),
        ),
    ]
