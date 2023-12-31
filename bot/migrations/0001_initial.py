# Generated by Django 4.2 on 2023-12-13 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название комнаты для игры')),
                ('price', models.CharField(max_length=200, verbose_name='Бюджет подарка')),
                ('registration_date', models.DateField(verbose_name='Период регистрации (до 12 по МСК)')),
                ('sending_date', models.DateField(verbose_name='Дата раздачи подарков (до 12 по МСК)')),
                ('tglink', models.CharField(max_length=200, verbose_name='Тг ссылка на комнату')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Игра',
                'verbose_name_plural': 'Игры',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя участника')),
                ('email', models.EmailField(max_length=254, verbose_name='Почта участника')),
                ('wishlist', models.TextField(max_length=300, verbose_name='Пожелания участника')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.event')),
                ('giver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='giver', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
            },
        ),
    ]
