import random
from datetime import datetime

from celery import Celery

from bot.lottery import lottery

app = Celery('runbot', broker='pyamqp://guest@localhost//', backend='rpc://')

@app.task
def lottery():
    lottery()

if __name__ == '__main__':
    lottery.apply_async(eta=datetime(2023, 12, 31, 23, 59, 59))
    app.start()