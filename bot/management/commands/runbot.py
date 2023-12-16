from datetime import datetime

from django.core.management.base import BaseCommand
from telebot import TeleBot, apihelper, types
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar
from validate_email_address import validate_email

from bot.tasks import lottery
from SecretSanta.celery import app as celery_app
from SecretSanta.settings import TELEGRAM_BOT_TOKEN

bot = TeleBot(TELEGRAM_BOT_TOKEN)
game_states = {}
user_states = {}


@bot.message_handler(commands=['organize'])
def handler_organize(message):
    markup = types.InlineKeyboardMarkup()
    create_game_button = types.InlineKeyboardButton('Создать игру', callback_data='create_game')
    markup.add(create_game_button)
    bot.send_message(message.chat.id, 'Организуй тайный обмен подарками, запусти праздничное настроение!', reply_markup=markup)
    user_states[message.from_user.id] = 'get_room_name'

@bot.message_handler(commands=['start'])
def handler_start(message):
    bot.send_message(message.chat.id, 'Замечательно, ты собираешься участвовать в игре: название c бюджетом и датой проведения')
    bot.send_message(message.chat.id, 'Введите имя')
    user_states[message.from_user.id] = 'get_name'

@bot.message_handler(func=lambda message: True)
def discuss_with_bot(message):
    user_id = message.from_user.id
    if user_id in user_states:
        current_state = user_states[user_id]
        if current_state == 'get_name':
            bot.send_message(message.chat.id, f'Приветствую вас {message.text}. Введите ваш email')
            user_states[user_id] = 'get_email'

        elif current_state == 'get_email':
            if validate_email(message.text):
                bot.send_message(message.chat.id, f'Спасибо Ваш email {message.text}')
                bot.send_message(message.chat.id, 'Напиши письмо Санте, что бы ты хотел?')
                user_states[user_id] = 'get_wish'
            else:
                bot.send_message(message.chat.id, 'Не верный формат email. Попробуйте еще раз')
                user_states[user_id] = 'get_email'

        elif current_state == 'get_wish':
            bot.send_message(message.chat.id, 'Превосходно, ты в игре! 31.12.2023 мы проведем жеребьевку и ты узнаешь имя и контакты своего тайного друга. Ему и нужно будет подарить подарок!')
            # TODO заменит дату на дату из бд, которую выбрал user
            lottery_end = lottery.apply_async(eta=datetime(2023, 12, 31, 23, 59, 59), app=celery_app)
            user_states[user_id] = 'wait_lottery'

        elif current_state == 'wait_lottery':
            print(user_states, current_state)
            result = lottery.AsyncResult(lottery_end.id)
            print('result', result)
            if result.ready():
                print('Результат:', result.result)
                bot.send_message(message.chat.id, 'Жеребьевка проведена! Твой тайный друг - {}.'.format(result.get()))
                user_states[user_id] = 'start_game'
            else:
                print('Состояние:', result.state)
                bot.send_message(message.chat.id, 'Жеребьевка еще не проведена. Подожди немного.')

        elif current_state == 'start_game':
            del user_states[user_id]

        elif current_state == 'get_room_name':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Да', callback_data='with_present'))
            markup.add(types.InlineKeyboardButton('Нет', callback_data='set_registration'))
            bot.send_message(message.chat.id, 'Будем вводить ограничение стоимости подарка?', reply_markup=markup)
            del user_states[user_id]
            
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так попробуйте еще раз')
        bot.send_message(message.chat.id, '/start')



@bot.callback_query_handler(func=lambda call: call.data == 'create_game')
def create_game(call):
    bot.send_message(call.message.chat.id, 'Придумай название для комнаты:')


@bot.callback_query_handler(func=lambda call: call.data == 'with_present')
def set_budget(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('До 500 рублей', callback_data='set_registration'))
    markup.add(types.InlineKeyboardButton('От 500 до 1000 рублей', callback_data='set_registration'))
    markup.add(types.InlineKeyboardButton('Больше 1000 рублей', callback_data='set_registration'))
    bot.send_message(call.message.chat.id, 'Выберите бюджет:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'set_registration')
def set_registration(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('До 25.12.2023', callback_data='set_sending_date'))
    markup.add(types.InlineKeyboardButton('До 31.12.2023', callback_data='set_sending_date'))
    bot.send_message(call.message.chat.id, 'Выбери период регистрации участников:(до 12.00 МСК)', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'set_sending_date')
def handle_calendar(call):
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
    bot.send_message(call.message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Ваш выбор {result}",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.message.chat.id, 'Отлично, Тайный Санта уже готовится к раздаче подарков! Комната НАЗВАНИЕ с БЮДЖЕТ и ПЕРИОД РЕГИСТРАЦИИ создана! Вот ссылка для участников игры, по которой они смогут зарегистрироваться.')
        bot.send_message(call.message.chat.id, 'https://t.me/dev_flower_shop_bot')


class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)