# Generated by Django 4.2 on 2023-12-17 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='event',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='giver',
        ),
        migrations.RemoveField(
            model_name='participant',
            name='receiver',
        ),
    ]
