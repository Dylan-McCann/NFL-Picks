# Generated by Django 4.2.15 on 2024-09-12 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poolapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='date',
        ),
        migrations.AddField(
            model_name='game',
            name='week',
            field=models.IntegerField(default=0),
        ),
    ]
