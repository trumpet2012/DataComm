# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 13:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('networking', '0003_device_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TraceHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hops', jsonfield.fields.JSONField()),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='networking.Device')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='networking.Session')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='networking.Device')),
            ],
        ),
    ]
