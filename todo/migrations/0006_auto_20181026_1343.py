# Generated by Django 2.0.6 on 2018-10-26 11:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0005_auto_20180901_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userfeed',
            name='post_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 26, 13, 43, 58, 396939)),
        ),
        migrations.AlterField(
            model_name='usermsg',
            name='post_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 10, 26, 13, 43, 58, 396939)),
        ),
    ]
