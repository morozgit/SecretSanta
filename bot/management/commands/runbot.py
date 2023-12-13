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


@bot.message_handler(commands=['organize'])
def hello_organize(message):
    bot.send_message(message.chat.id, 'Сервис для обмена новогодними подарками')
    user_states[message.from_user.id] = 'start_game'


@bot.message_handler(func=lambda message: True)
def create_game(message):
    user_id = message.from_user.id
    if user_id in user_states:
        current_state = user_states[user_id]
        if current_state == 'start_game':
            bot.send_message(message.chat.id, f'Организуй тайный обмен подарками, запусти праздничное настроение!')
            user_states[user_id] = 'create_game'

        elif current_state == 'create_game':
            bot.send_message(message.chat.id, f'Придумай название для комнаты:')
            user_states[user_id] = 'get_room_name'

        elif current_state == 'get_room_name':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('Да'))
            markup.add(types.KeyboardButton('Нет'))
            bot.send_message(message.chat.id, 'Будем вводить ограничение стоимости подарка?', reply_markup=markup)
            user_states[user_id] = 'set_budget'

        elif current_state == 'set_budget':
            if message.text == "Да":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(types.KeyboardButton('До 500 рублей'))
                markup.add(types.KeyboardButton('От 500 до 1000 рублей'))
                markup.add(types.KeyboardButton('Больше 1000 рублей'))
                bot.send_message(message.chat.id, 'Выберите бюджет:', reply_markup=markup)
                user_states[user_id] = 'set_registration'
            else:
                user_states[user_id] = 'set_registration'
        
        elif current_state == 'set_registration':
            bot.send_message(message.chat.id, 'Выбери период регистрации участников:(до 12.00 МСК)')
            user_states[user_id] = 'set_sending_date'
            
        elif current_state == 'set_sending_date':
            #проверить дату
            bot.send_message(message.chat.id, 'Напиши дату вручения подарков:')
            user_states[user_id] = 'finish'

        elif current_state == 'finish':
            #проверить дату
            bot.send_message(message.chat.id, 'Отлично, Тайный Санта уже готовится к раздаче подарков! Комната НАЗВАНИЕ с БЮДЖЕТ и ПЕРИОД РЕГИСТРАЦИИ создана! Вот ссылка для участников игры, по которой они смогут зарегистрироваться.')
   
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так попробуйте еще раз')
        bot.send_message(message.chat.id, '/organize')


class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)