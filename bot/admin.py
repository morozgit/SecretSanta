import random

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, re_path, reverse
from django.utils.html import format_html

from bot.lottery import lottery
from bot.management.commands.runbot import bot
from bot.management.commands.signals import drawing_of_lots_signal

from .models import Event, Participant, ResultLottery


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'price',
                    'registration_date',
                    'sending_date',
                    'tglink',
                    'admin',
                    'account_actions')
    search_fields = ('name',
                     'price',
                     'registration_date',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<account_id>.)$',
                self.admin_site.admin_view(self.process_deposit),
                name='account-deposit',
            ),
        ]
        return custom_urls + urls
    
    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Жеребьевка</a> ',
            reverse('admin:account-deposit', args=[obj.pk]),
        )
    account_actions.short_description = 'Account Actions'
    account_actions.allow_tags = True

    def process_deposit(self, request, *args, **kwargs):
        id = kwargs['account_id']
        print(id)
        lottery(id)
        drawing_of_lots_signal.send(sender=self.__class__, request=request)
        self.message_user(request, "Жеребьевка проведена успешно!")
        return HttpResponseRedirect("./")

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'email',
                    'game')
    search_fields = ('name',
                     'email',
                     'game')
    
@admin.register(ResultLottery)
class ResultLotteryAdmin(admin.ModelAdmin):
    list_display = ('giver_name', 'receiver_name', 'giver_present', 'receiver_present')
    search_fields = ('giver_name', 'receiver_name')