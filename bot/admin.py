from django.contrib import admin

from .models import Event, Participant


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
                    'email')
    search_fields = ('name',
                     'email')