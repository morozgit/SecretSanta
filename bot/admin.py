import random

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, re_path
from django.utils.safestring import mark_safe

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
                    'admin')
    search_fields = ('name',
                     'price',
                     'registration_date',)




@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'email',
                    )
    search_fields = ('name',
                     'email')
    
    change_list_template = "admin/model_change_list.html"
 
    def get_urls(self):
        urls = super(ParticipantAdmin, self).get_urls()
        custom_urls = [
            re_path(r'^drawing_of_lots/$', self.drawing_of_lots, name='drawing_of_lots'), ]
        return custom_urls + urls
 
    def drawing_of_lots(self, request):
        lottery()
        drawing_of_lots_signal.send(sender=self.__class__, request=request)
        self.message_user(request, "Жеребьевка проведена успешно!")
        return HttpResponseRedirect("../")
    
@admin.register(ResultLottery)
class ResultLotteryAdmin(admin.ModelAdmin):
    list_display = ('giver_name', 'receiver_name')
    search_fields = ('giver_name', 'receiver_name')