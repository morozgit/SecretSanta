from django.core.management.base import BaseCommand
from telebot import TeleBot, apihelper, types
from validate_email_address import validate_email

from SecretSanta.settings import TELEGRAM_BOT_TOKEN

bot = TeleBot(TELEGRAM_BOT_TOKEN)
game = {}
user_states = {}


@bot.message_handler(commands=['start'])
def send_link(message):
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
            user_states[user_id] = 'start_game'
        
        elif current_state == 'start_game':
            del user_states[user_id]
            
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так попробуйте еще раз')
        bot.send_message(message.chat.id, '/start')


class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)