# Generated by Django 3.1.7 on 2021-05-04 16:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20210503_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pollmodel',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 4, 16, 22, 7, 207632)),
        ),
    ]
