# Generated by Django 4.2 on 2023-12-19 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_event_tg_chat_id_alter_participant_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultlottery',
            name='giver_present',
            field=models.CharField(default='', max_length=100, verbose_name='Подарок Кто дарит'),
        ),
        migrations.AddField(
            model_name='resultlottery',
            name='receiver_present',
            field=models.CharField(default='', max_length=100, verbose_name='Подарок Получатель'),
        ),
    ]
