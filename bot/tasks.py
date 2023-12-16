import random

from celery import Celery

from bot.lottery import lottery

from .models import Participant

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def lottery():
    lottery()