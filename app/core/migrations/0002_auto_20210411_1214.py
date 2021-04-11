# Generated by Django 3.1.7 on 2021-04-11 10:14

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultPageModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('references', django_mysql.models.ListCharField(models.CharField(max_length=255), max_length=13005, size=50)),
            ],
        ),
        migrations.DeleteModel(
            name='AbstractModel',
        ),
    ]
