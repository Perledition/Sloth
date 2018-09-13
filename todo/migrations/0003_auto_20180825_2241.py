# Generated by Django 2.0.6 on 2018-08-25 20:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0002_auto_20180825_2240'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirstFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_time', models.DateTimeField(default=datetime.datetime.now)),
                ('how', models.CharField(default='Angesprochener Tester', max_length=21)),
                ('impress', models.IntegerField(default=0)),
                ('impact', models.IntegerField(default=0)),
                ('opinion', models.CharField(max_length=300)),
                ('mail', models.EmailField(default='admin@sloth.de', max_length=254)),
            ],
        ),
        migrations.AlterField(
            model_name='userfeed',
            name='post_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 25, 22, 41, 53, 687174)),
        ),
        migrations.AlterField(
            model_name='usermsg',
            name='post_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 8, 25, 22, 41, 53, 687174)),
        ),
    ]
