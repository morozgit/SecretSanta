# SecretSantaBot

Телеграм бот для проведения игры Тайного Санты

## Окружение

### Требования к установке

Python 3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2) для установки
зависимостей:

```bash
$ pip install -r requirements.txt
``` 

Создайте `.env` файл рядом с `manage.py` и добавьте:

`TELEGRAM_BOT_TOKEN='django secret key'` - токен от телеграм бота. 


## Сценарий использования бота

#### Запуск проекта

- Сделайте миграцию, создайте суперюзера и запустите сервер Django

```bash
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

- и параллельно запустите работу телеграм бота

```bash
$ python manage.py runbot
```

#### Создание игры и проведение жеребьёвки

Начните создание команты в телеграм боте с помощью команды

```
/organize
```

После этого разошлите участникам ссылку на бота с названием комнаты. После регистрации участников дождитесь даты жеребьёвки или зайдите в админку django http://127.0.0.1:8000/admin/ и нажмите на кнопку.
