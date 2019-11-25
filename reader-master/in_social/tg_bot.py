import os
import json
import telebot
from telebot import types

import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
MAIN_BOT = telebot.TeleBot('843017891:AAHwQI-y7bT_UaYYAOsb4ICYx8x7YQYGhAo')
SERVER_URL = 'http://reader.heck.today/'
FLAG_OF_REFERENCE = dict()

def get_token_api():
    """
    Функция возвращающая token из файла для POST-запросов API
    :return: token
    """
    files = open('/var/www/reader/reader/token.txt')
    return files.readline()


def create_post(date):
    """
    :param date: Все параметры пользователя
    :return: 1 в случае ошибки подключения
    """
    sess = requests.Session()
    sess.get(SERVER_URL + '/')
    data = dict()
    data['params'] = date
    data['params']['who_is'] = 'tg'
    data['token'] = get_token_api()
    data = json.dumps(data)
    token = 'csrfmiddlewaretoken'
    crs = 'csrftoken'
    answer = sess.post(SERVER_URL + "/api/", data={'json': data, token: str(sess.cookies.get(crs))})
    if answer.status_code == 404:
        return 1
    return 0


@MAIN_BOT.message_handler(commands=['start', 'help'])
def start(user_data):
    """
    :param user_data: все параметры чата
    :return: отсутствует
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
    part_one = ". Вставьте его в настройках сайта."
    part_two = " Вы можете использовать команду '/save'"
    part_three = ", чтобы сохранить ссылку."
    phrase = part_one + part_two + part_three
    uid = "Ваш id - "
    streng = uid + str(user_data.chat.id) + phrase
    message = MAIN_BOT.send_message(user_data.chat.id, streng, reply_markup=keyboard)

    MAIN_BOT.register_next_step_handler(message, choice)


@MAIN_BOT.message_handler(commands=['/save'])
def choice(user_data):
    """
    :param user_data: все параметры чата
    :return: отсутствует
    """
    if user_data.text == '/start' or user_data.text == '/help':
        start(user_data)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        w_tag = 'С тегами.'
        wo_tag = 'Без тегов.'
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in [w_tag, wo_tag]])
        choose = "Выберите режим."
        message = MAIN_BOT.send_message(user_data.chat.id, choose, reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, name)


def name(user_data):
    """
    :param user_data: все параметры чата
    :return: отсутствует
    """
    markup = types.ReplyKeyboardRemove(selective=False)
    if user_data.text == '/start' or user_data.text == '/help':
        start(user_data)
    elif user_data.text == 'С тегами.':
        ref = "Ссылка:"
        message = MAIN_BOT.send_message(user_data.chat.id, ref, reply_markup=markup)
        MAIN_BOT.register_next_step_handler(message, link)
    elif user_data.text == 'Без тегов.':
        ref = "Ссылка:"
        message = MAIN_BOT.send_message(user_data.chat.id, ref, reply_markup=markup)
        MAIN_BOT.register_next_step_handler(message, just_link)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
        wrong = "Неправильный формат ввода..."
        message = MAIN_BOT.send_message(user_data.chat.id, wrong, reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, choice)


def just_link(user_data):
    """
    SENDING JUST A LINK
    :param user_data: все параметры чата
    :return: отсутствует
    """
    data = ({'title': '', 'url': user_data.text, 'uid': user_data.chat.id, 'tags': []})
    if create_post(data):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
        part_one = "Ошибка... Проверьте, вставили ли вы ваш id"
        part_two = " в настройках сайта и попробуйте снова."
        phrase = part_one + part_two
        message = MAIN_BOT.send_message(user_data.chat.id, phrase, reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, choice)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
        ready = "Готово."
        message = MAIN_BOT.send_message(user_data.chats.id, ready, reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, choice)


def link(user_data):
    """
    SENDING LINK WITHOUT A TAG
    :param user_data: все параметры чата
    :return: отсутствует
    """
    MAIN_BOT.register_next_step_handler(MAIN_BOT.send_message(user_data.chat.id, "Тег:"), tag)
    FLAG_OF_REFERENCE['ref'] = user_data.text


def tag(user_data):
    """
    SENDING A TAG
    """
    tage = list(user_data.text.split())
    ref = FLAG_OF_REFERENCE['ref']
    FLAG_OF_REFERENCE.clear()
    data = ({'title': '', 'url': ref, 'uid': user_data.chat.id, 'tags': tage})

    if create_post(data):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
        part_one = "Ошибка... Проверьте, вставили ли вы ваш id"
        part_two = " в настройках сайта и попробуйте снова."
        phrase = part_one + part_two
        message = MAIN_BOT.send_message(user_data.chat.id, phrase, reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, choice)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(iterator) for iterator in ['/save']])
        message = MAIN_BOT.send_message(user_data.chat.id, "Готово.", reply_markup=keyboard)
        MAIN_BOT.register_next_step_handler(message, choice)


MAIN_BOT.polling(none_stop=True, timeout=20)
