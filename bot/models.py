from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название комнаты для игры")
    price = models.CharField(max_length=200, verbose_name="Бюджет подарка")
    registration_date =  models.DateField(verbose_name="Период регистрации (до 12 по МСК)")
    sending_date = models.DateField(verbose_name="Дата раздачи подарков (до 12 по МСК)")
    tglink = models.CharField(max_length=200, verbose_name="Тг ссылка на комнату")
    admin = models.ForeignKey(User, related_name='admin', on_delete=models.CASCADE)

    def __str__(self):
        return f'Игра {self.name}'

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"


class Participant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя участника")
    email = models.EmailField( verbose_name="Почта участника")
    wishlist = models.TextField(max_length=300, verbose_name="Пожелания участника")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"


class ResultLottery(models.Model):
    giver_name = models.CharField(max_length=100, verbose_name="Кто дарит")
    receiver_name = models.CharField(max_length=100, verbose_name="Получатель")

    def __str__(self):
        return f'{self.giver_name}, {self.receiver_name}'

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"