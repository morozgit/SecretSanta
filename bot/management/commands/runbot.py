from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from telebot import TeleBot, apihelper, types
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar
from validate_email_address import validate_email

from bot.models import Event, Participant, ResultLottery
from bot.tasks import lottery
from SecretSanta.celery import app as celery_app
from SecretSanta.settings import TELEGRAM_BOT_TOKEN

bot = TeleBot(TELEGRAM_BOT_TOKEN)
game = {}
user_data = {}
user_states = {}


@bot.message_handler(commands=['organize'])
def handler_organize(message):
    game['game_admin'], created = User.objects.get_or_create(username='temchmorozov')
    markup = types.InlineKeyboardMarkup()
    create_game_button = types.InlineKeyboardButton('Создать игру', callback_data='create_game')
    markup.add(create_game_button)
    bot.send_message(message.chat.id, 'Организуй тайный обмен подарками, запусти праздничное настроение!', reply_markup=markup)
    user_states[message.from_user.id] = 'get_room_name'

@bot.message_handler(commands=['start'])
def handler_start(message):
    games = Event.objects.all()
    if games:
        markup = types.InlineKeyboardMarkup()
        for game_id, game in enumerate(games):
            choice_game_button = types.InlineKeyboardButton(game.name, callback_data=f'choice_game:{game_id+1}')
            markup.add(choice_game_button)

        bot.send_message(message.chat.id, 'Выберите игру:', reply_markup=markup)
        user_states[message.from_user.id] = 'get_name'
    else:
        bot.send_message(message.chat.id, 'Игра еще не создана')
    

@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == 'choice_game')
def choice_game(call):
    current_game = Event.objects.get(id=call.data.split(':')[1])
    bot.send_message(call.message.chat.id, f'Замечательно, ты собираешься участвовать в игре: {current_game.name} c бюджетом {current_game.price} и датой проведения {current_game.registration_date}')
    bot.send_message(call.message.chat.id, 'Введите имя')

@bot.message_handler(func=lambda message: True)
def discuss_with_bot(message):
    user_id = message.from_user.id
    if user_id in user_states:
        current_state = user_states[user_id]
        if current_state == 'get_name':
            user_data['name'] = message.text
            bot.send_message(message.chat.id, f'Приветствую вас {message.text}. Введите ваш email')
            user_states[user_id] = 'get_email'

        elif current_state == 'get_email':
            if validate_email(message.text):
                user_data['email'] = message.text
                bot.send_message(message.chat.id, f'Спасибо Ваш email {message.text}')
                bot.send_message(message.chat.id, 'Напиши письмо Санте, что бы ты хотел?')
                user_states[user_id] = 'get_wish'
            else:
                bot.send_message(message.chat.id, 'Не верный формат email. Попробуйте еще раз')
                user_states[user_id] = 'get_email'

        elif current_state == 'get_wish':
            user_data['wishlist'] = message.text
            registration_date = Event.objects.values_list('registration_date', flat=True).get(id=1)
            bot.send_message(message.chat.id, f'Превосходно, ты в игре! {registration_date} мы проведем жеребьевку и ты узнаешь имя и контакты своего тайного друга. Ему и нужно будет подарить подарок!')
            lottery_end = lottery.apply_async(eta=registration_date, app=celery_app)
            user_states[user_id] = 'wait_lottery'
            Participant.objects.create(name=user_data['name'],
                                       email=user_data['email'],
                                       wishlist=user_data['wishlist'],
                                       )

        elif current_state == 'wait_lottery':
            result = celery_app.AsyncResult(lottery_end.id)
            print('result', result)
            if result.ready():
                receiver_name = ResultLottery.objects.values_list('receiver_name', flat=True).get(id=1)
                bot.send_message(message.chat.id, 'Жеребьевка проведена! Твой тайный друг - {receiver_name}.'.format(result.get()))
                user_states[user_id] = 'start_game'
            else:
                print('Состояние:', result.state)
                bot.send_message(message.chat.id, 'Жеребьевка еще не проведена. Подожди немного.')

        elif current_state == 'start_game':
            del user_states[user_id]

        elif current_state == 'get_room_name':
            game['name'] = message.text
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Да', callback_data='with_present'))
            markup.add(types.InlineKeyboardButton('Нет', callback_data=f'set_registration:{None}'))
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
    markup.add(types.InlineKeyboardButton('До 500 рублей', callback_data='set_registration:-500'))
    markup.add(types.InlineKeyboardButton('От 500 до 1000 рублей', callback_data='set_registration:500-1000'))
    markup.add(types.InlineKeyboardButton('Больше 1000 рублей', callback_data='set_registration:1000+'))
    bot.send_message(call.message.chat.id, 'Выберите бюджет:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == 'set_registration')
def set_registration(call):
    game['price'] = call.data.split(':')[1]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('До 25.12.2023', callback_data='set_sending_date:2023-12-25'))
    markup.add(types.InlineKeyboardButton('До 31.12.2023', callback_data='set_sending_date:2023-12-31'))
    bot.send_message(call.message.chat.id, 'Выбери период регистрации участников:(до 12.00 МСК)', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == 'set_sending_date')
def handle_calendar(call):
    game['registration_date'] = call.data.split(':')[1]
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
    bot.send_message(call.message.chat.id, 'Выберите дату отправки подарка', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').process(call.data)
    if not result and key:
        bot.edit_message_text('Выберите дату отправки подарка',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
        
    elif result:
        game['sending_date'] = result
        bot.edit_message_text(f"Ваш выбор {result}",
                              call.message.chat.id,
                              call.message.message_id)
        bot.send_message(call.message.chat.id, 'Отлично, Тайный Санта уже готовится к раздаче подарков! Комната НАЗВАНИЕ с БЮДЖЕТ и ПЕРИОД РЕГИСТРАЦИИ создана! Вот ссылка для участников игры, по которой они смогут зарегистрироваться.')
        bot.send_message(call.message.chat.id, 'https://t.me/dev_flower_shop_bot')

        Event.objects.create(name=game['name'],
                            price=game['price'],
                            registration_date=game['registration_date'],
                            sending_date=game['sending_date'],
                            tglink='https://t.me/dev_flower_shop_bot',
                            admin=game['game_admin'])

class Command(BaseCommand):
    help = 'телеграм бот'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)