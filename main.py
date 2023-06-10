""" Телеграм Бот """
# pylint: disable=C0103


from random import choice, randint
from datetime import datetime
import os.path

import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Text

from bs4 import BeautifulSoup as BS
from requests import get

from fake_useragent import UserAgent
import urllib3

from dotenv import load_dotenv


headers = {'User_Agent': UserAgent().random}
HttpPoolManager = urllib3.PoolManager()


# загрузка переменных окружения
if os.path.exists('.env'):
    load_dotenv()

bot = aiogram.Bot(token=os.getenv('TELEGRAM_API_TOKEN'))
dp = aiogram.Dispatcher(bot)


def today():
    """ Возвращает дату и время выполнения функции в формате '%d-%m-%Y   %H:%M'
        Returns the date and time of the function in the format '%d-%m-%Y   %H:%M' """
    return datetime.today().strftime('%d-%m-%Y   %H:%M')


def get_random_fact():
    """ Возвращает текст и ссылку случайного факта
        Returns the text and link of a random fact """
    html = BS(get('https://i-fakt.ru', timeout=5).content, 'html.parser')
    fact = choice(html.find_all(class_='p-2 clearfix'))

    return fact.text, fact.a.attrs['href']


def get_random_event():
    """ Возвращает текст и ссылку случайного события
        Returns the text and link of a random event """
    html = BS(get('https://kudago.com/msk/festival/', timeout=5).content, 'html.parser')
    event = choice(html.find_all(class_='post-title'))

    return event.span.text, event.a['href']


def get_random_joke():
    """ Возвращает текст случайного анекдота
        Returns the text of a random joke """
    url = 'https://randstuff.ru/joke/'
    return BS(get(url, timeout=5).content, 'html.parser').find('td').get_text()


def get_joke_of_the_day():
    """ Возвращает текст анекдота дня
        Returns the text of the joke of the day """
    url = 'https://randstuff.ru/joke/fav/'
    return BS(get(url, timeout=5).content, 'html.parser').find('td').get_text()


def get_currencies():
    """ Возвращает текст курса валют 'Банк России'
        Returns the text of the exchange rate 'Bank of Russia' """
    today_ = datetime.today()
    today_1 = datetime.strftime(today_, '%d/%m/%Y')
    parameters = {
        'date_req': today_1
    }

    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    xml = BS(get(url, timeout=5, params=parameters).content, 'lxml')
    currencies = xml.findAll('valute')
    all_currencies = ''
    for currencies_xml in currencies:
        currencies_name = currencies_xml.find('name').text
        value_value = currencies_xml.find('value').text
        all_currencies += f'• {currencies_name} цена: {value_value} рублей;\n'

    return all_currencies


def get_film():
    """ Возвращает текст, фото (img) и ссылку случайного фильма
        Returns text, photo (img) and link of a random movie """
    url = 'https://www.kinoafisha.info/rating/movies/?page='
    html = BS(get(f'{url}{randint(1, 10)}', timeout=5).content, 'html.parser')
    film = choice(html.find_all(
        class_='movieList_item movieItem movieItem-rating movieItem-position'
    ))

    film_img = film.find('img')['data-picture']
    film_text = film.find('a', class_='movieItem_title').text
    film_url = film.a['href']

    return film_text, film_img, film_url


def get_game():
    """ Возвращает текст, ссылку и фото (img) случайной игры из лучших
        Returns text, link and photo (img) of a random game from the best """
    url = 'https://stopgame.ru/games/pc/best?year_start=2000&p='

    html = BS(get(f'{url}{randint(1, 15)}', timeout=5).content, 'html.parser')
    game = choice(html.find_all(class_='_card_13hsk_1'))
    game_url = f'https://stopgame.ru/{game["href"]}'
    html_ = BS(get(game_url, timeout=5).content,  'html.parser')

    game_text = html_.find(class_='_title_qrsvr_270').text
    game_text_info = html_.find(class_='_info-container__top_sh7r2_1').text
    game_img = html_.find('img', class_='_image_sh7r2_31')['src']

    return game_text, game_text_info, game_url, game_img


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    """ Команда 'старт'
        The 'start' command """
    welcome_text = \
        'Добрый день! :)\nВот что я умею:\n' \
        '/start - Добрый день! Начать работу\n' \
        '/game - Показать случайную игру из лучших\n' \
        '/film - Показать случайный фильм\n' \
        '/cat - Показать случайную фоточку с котиком\n' \
        '/fact -Показать рандомный факт\n' \
        '/event - Показать интересный фестиваль\n' \
        '/joke - Показать случайный анекдот\n' \
        '/currencies - Котировка курса валюты\n' \
        '/donat - донат автору бота ;)\n' \
        'или можете просто нажимать\nна кнопки для удобства ;)'

    keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True, one_time_keyboard=False)

    buttons = [
        types.KeyboardButton('Игры'),
        types.KeyboardButton('Фильмы'),
        types.KeyboardButton('Котики'),
        types.KeyboardButton('Факты'),
        types.KeyboardButton('Событие'),
        types.KeyboardButton('Анекдоты'),
        types.KeyboardButton('Валюты')

    ]
    keyboard.add(*buttons)

    await message.reply(
        welcome_text, reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id} - start\n')


@dp.message_handler(commands=['fact'])
@dp.message_handler(Text(equals='Факты'))
async def send_fact(message: types.message):
    """ Команда случайного факта функции get_random_fact()
        The random fact command of the function get_random_fact() """
    event, url = get_random_event()
    event_text = [
        'Ловите очередной факт:\n',
        'Получите рандомный факт:\n',
        'Вот Вам какой-то интересный факт:\n'
    ]

    rand_event_text = str(choice(event_text))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text="Перейти)", url=url)
    keyboard.add(buttons)

    await message.reply(
        rand_event_text +
        event, reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id}: {event} - Факты\n')


@dp.message_handler(commands=['event'])
@dp.message_handler(Text(equals='Событие'))
async def send_festival(message: types.message):
    """ Команда случайного события функции get_random_event()
        Function random event command get_random_event() """
    festival, url = get_random_event()
    festival_text = [
        'Ловите очередное событие:\n',
        'Получите случайное событие:\n',
        'Вот Вам какой-то интересное событие:\n'
        'Как Вам это событие? \n'
    ]

    rand_festival_text = str(choice(festival_text))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text="Перейти)", url=url)
    keyboard.add(buttons)

    await message.answer(
        rand_festival_text +
        festival, reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id}: {festival} - Событие\n')


@dp.message_handler(commands=['joke'])
@dp.message_handler(Text(equals='Анекдоты'))
async def send_joke(message: types.message):
    """ Команда выведения кнопок случайного анекдота и анекдота дня
        функции send_random_value()
        The command for displaying random joke and joke of the day buttons
        send_random_value() """
    messages = 'Анекдоты и шутки ;)'
    buttons = [
        types.InlineKeyboardButton(text="Шуточка ;)", callback_data='joke'),
        types.InlineKeyboardButton(text="Анекдот дня ;)", callback_data='joke_of_the_day')
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    await message.answer(
        messages, reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id}: {messages} - Анекдоты\n')


@dp.callback_query_handler(text="joke")
async def send_random_value(call: types.CallbackQuery):
    """ Кнопка случайного анекдота функции send_joke()
        Возвращает функцию get_random_joke()
        Random joke button function send_joke()
        Returns the function get_random_joke() """
    await call.message.answer(get_random_joke())

    print(f'{today()}: {get_random_joke()} - Анекдот\n')


@dp.callback_query_handler(text="joke_of_the_day")
async def send_random_values(call: types.CallbackQuery):
    """ Кнопка анекдота дня функции send_joke()
        Возвращает функцию get_joke_of_the_day()
        Anecdote button of the day function send_joke()
        Returns the function get_joke_of_the_day() """
    await call.message.answer(get_joke_of_the_day())

    print(f'{today()}: {get_joke_of_the_day()} - Анекдот дня\n')


@dp.message_handler(commands=['film'])
@dp.message_handler(Text(equals='Фильмы'))
async def send_film(message: types.message):
    """ Команда случайного фильма функции get_film()
        Random Movie command functions get_film() """
    title, img_src, url = get_film()
    resp = HttpPoolManager.request('GET', img_src)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text="Ссылочка)", url=url)
    keyboard.add(buttons)

    await bot.send_photo(
        message.chat.id,
        photo=resp.data,
        caption=title,
        reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id}: {title}; {url} - Фильмы\n')


@dp.message_handler(commands=['game'])
@dp.message_handler(Text(equals='Игры'))
async def send_game(message: types.message):
    """ Команда случайной игры из лучших функции get_game()
        Random game command or the best get_game() functions """
    text, text_info, url, img = get_game()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text="Ссылочка)", url=url)
    keyboard.add(buttons)

    await bot.send_photo(
        message.chat.id,
        photo=img,
        caption=text + text_info,
        reply_markup=keyboard
    )

    print(f'{today(), message.from_user.username, message.from_user.id}; {text}; {url} - Игры\n')


@dp.message_handler(commands=['cat'])
@dp.message_handler(Text(equals='Котики'))
async def get_cat(message: types.message):
    """ Команда случайной фотографии с котиками
        Command random photo with cats """
    await bot.send_photo(
        message.chat.id,
        photo=get('http://thecatapi.com/api/images/get?format=src', timeout=3).content
    )

    print(f'{today(), message.from_user.username, message.from_user.id} - Котики\n')


@dp.message_handler(commands=['currencies'])
@dp.message_handler(Text(equals='Валюты'))
async def send_currencies(message: types.message):
    """ Команда курса валют функции get_currencies()
        Currency Exchange Rate command functions get_currencies()"""
    all_currencies = get_currencies()

    await message.reply(
        all_currencies
    )

    print(f'{today(), message.from_user.username, message.from_user.id} - Валюты\n')


@dp.message_handler(commands=['donat'])
async def donat(message: types.Message):
    """ Команда донатов и пожеланий
        Command of donations and wishes """
    donats = (
        'Очень рад Вашим донатам, они помогут улучшить мои умения и навыки, '
        'а также самого бота !\n'
        'Не забывайте подписывать от кого ( или можно анонимно ;) ), '
        'а также писать свои пожелания или что стоит улучшить ( в самом данате ) !\n'
        'Большое спасибо, сам донат вы можете перевести на карту банка Тинькофф:\n\n'
        '5536914143288433'
    )

    await message.reply(
        donats
    )

    print(f'{today(), message.from_user.username, message.from_user.id} - Донаты\n')


@dp.message_handler()
async def get_photo(message: types.Message):
    """ Команда выведения ошибки при неверной команде от пользователя,
        команда показа создателей бота
        The command to output an error with an incorrect command from the user,
        the command to show the creators of the bot """
    if 'на хуй' in message.text or 'нахуй' in message.text:
        url = 'https://yandex.ru/images/search?lr=65&source=serp&stype=image&text=иди%20нахуй%20)'
        html = BS(get(url, timeout=5).content,  'html.parser')
        error = choice(html.find_all(class_='serp-item__link'))
        errors = f"https:{error.find('img')['src']}"

        await bot.send_photo(
            message.chat.id,
            photo=errors
        )

        print(f'{today(), message.from_user.username, message.from_user.id}\n{errors} - ошибка\n')

    elif '/создатели' in message.text:
        error = 'разраб: криворукий гей\nнаставник: ахуенный гей'

        await message.reply(
            error
        )

        await bot.send_photo(
            message.chat.id,
            photo=types.InputFile('Developers.jpg'), caption="Вот эти два гея ;)"
        )

        print(
            f'{today(), message.from_user.username, message.from_user.id}: {message.text}'
            f' - создатели\n'
        )

    elif '/' in message.text:
        error = 'Простите, я не понимаю Вашу команду :('

        await message.reply(
            error
        )

        print(
            f'{today(), message.from_user.username, message.from_user.id}: {message.text} '
            f'- ошибка\n'
        )


if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
