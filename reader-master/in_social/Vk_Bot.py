"""
Модуль ВК бота.
"""

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import json
import requests

server_url = 'http://reader.heck.today/'


def get_token_api():
    """
    Функция возвращающая token из файла на сервере для выполнения POST-запросов к API
    :return: token
    """
    f = open('/var/www/reader/reader/token.txt', 'r')
    return f.readline()


class VKBot(object):
    """
    Класс создания бота для одного пользователя
    """
    def __init__(self):
        self.event = None
        self.state = None
        self.vk_session = vk_api.VkApi(
            token='0e38fab87c3a1becb233040949c75856764ac56651834b73d0760a9cf5fedac99bcee1dd0e781c15edca6')
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        self.user_state = {}
        self.keyboard = None
        self.post = None
        self.tag = None

    def create_post(self, d):
        sess = requests.Session()
        sess.get(server_url + '/')
        data = dict()
        data['params'] = d
        data['params']['who_is'] = 'vk'
        data['token'] = get_token_api()
        data = json.dumps(data)
        answer = sess.post(
            server_url+"/api/",
            data={'json': data, 'csrfmiddlewaretoken': str(sess.cookies.get('csrftoken'))}
        )
        print(answer)
        return answer.status_code

    def send_message(self, stage):
        stages_messages = {
            'starting': 'Привет. Напиши "/start", чтобы начать &#128075;',
            'ready': 'Готов к работе. Отправь мне ссылку или пост &#128526;',
            'link_with_tag_saver1':
                'Хорошо, переходим к добавлению тэгов, отправь ссылку или пост &#9997;',
            'link_with_tag_saver2':
                'Впишите теги через пробел &#9997;',
            'return_to_normal': 'Хорошо, вернемся в обычное сохранение ссылок &#9194;',
            'end': 'Хорошо, закончили. Напиши "/start", чтобы начать заново &#9194; ',
            'error_1': 'Прости, какая-то ошибка ❌',
            'error_no_user':
                'Не нашёл кому сохранять.\n Убедиcь, что на сайт добавлен аккаунт Вк ❌',
            'ok': 'Я сохранил ✅',
            'help': 'Кратко о нашем проекте : \n'
                    'Наш бот будет сохранять абсолютно все ссылки на посты , которые вы ему присылаете.\n'
                    'Так же вы можете вручную кидать ссылки с тэгами и без.\n'
                    'Для того, чтобы наш бот работал, пожалуйста, '
                    'Зарегистрируйтесь на нашем официальном сайте по адресу http://92.53.104.52, \n'
                    'а также добавьте ваш аккаунт в настройках аккаунтов',
            'error_2': 'Прости, какая-то ошибка ❌',
            'ok_1': 'Я сохранил ✅\nНапиши /start, чтобы вновь начать работу',

        }
        stages_keyboards = {
            'starting': ['/start', '/help'],
            'ready': ['Add link with tag', 'Cancel'],
            'link_with_tag_saver1': ['Cancel'],
            'link_with_tag_saver2': ['Cancel'],
            'return_to_normal': ['Add link with tag', 'Cancel'],
            'end': ['/start', '/help'],
            'error_1': ['Cancel'],
            'error_no_user': ['Add link with tag', 'Cancel'],
            'ok': ['Add link with tag', 'Cancel'],
            'help': ['/start', '/help'],
            'error_2': ['Add link with tag', 'Cancel'],
            'ok_1': ['/start'],
        }
        keyboard = vk.get_keyboard(label=stages_keyboards[stage])
        if not stages_keyboards[stage]:
            self.vk.messages.send(user_id=self.event.user_id, message=stages_messages[stage],
                                  random_id=get_random_id())
        else:
            self.vk.messages.send(user_id=self.event.user_id, message=stages_messages[stage],
                                  random_id=get_random_id(),
                                  keyboard=keyboard)

    def answer(self, data):
        code = self.create_post(data)
        if code == 404:
            self.send_message('error_no_user')
        elif code == 200 or code == 500:
            self.send_message('ok')
        else:
            self.send_message('error_2')
        return 0

    def checked_on_false_messenge(self, messenge, *context):
        if messenge in context:
            return True
        return False

    """
    функция перехода к новому состояни ( патерн состояния )
    """
    def change_state(self, new_state):
        self.state = new_state

    """
    функция процесса обработки ивента
    присваивание новых переменных
    """
    def process_event(self, event):
        u_id = event.user_id
        user_state = self.user_state.get(u_id, HiState())
        user_state.process_event(event, self)
        new_state = user_state.get_next_state()
        self.user_state[u_id] = new_state

    """
    функция создания кнопки 
    :param label: текст кнопки
    :param color: цвет кнопки
    :param playload: хз
    """

    def get_button(self, label, color, payload=""):
        return {
            'action': {
                'type': "text",
                'payload': json.dumps(payload),
                'label': label
            },
            'color': color
        }

    """
    функция получения цвета
    :param id: количество цветов
    """
    def get_color(self, id):
        color = {0: 'positive', 1: 'negative', 2: 'primary'}
        return color[id]

    """
    функция создания клавиатуры 
    :param label: тексты кнопок 
    """

    def get_keyboard(self, label):

        button = []
        for i in range(len(label)):
            button.append(vk.get_button(label=label[i], color=vk.get_color(i)))
        vk.keyboard = {
            'one_time': False,
            'buttons': [
                button
            ]
        }
        vk.keyboard = json.dumps(vk.keyboard)
        return vk.keyboard

    """
    функция перевода клавиатуры в json вид 
    """
    def to_str(self, keyboard):
        keyboard = json.dumps(keyboard)
        return keyboard


"""
Здесь используется патерн состояния пота
Имеется состояния :
Histate - состояние приведствия 
WaitForWork - состояние ожидания работы 
WorkState - состояние работы 
StateAddTag - состояние добавление тэга к ссылке (вручную )
SateAddLinkWithTag - состояние добавление ссылки с тэгом ( вручную )
"""


class BotState(object):
    def process_event(self, event, vk_bot):
        pass

    def get_next_state(self):
        pass


class HiState(BotState):

    def process_event(self, event, vk_bot):
        try:
            if event.text:
                vk_bot.event = event
                vk_bot.send_message('starting')
        except Exception:
            try:
                vk_bot.send_message('error_2')
            except Exception:
                pass

    def get_next_state(self):
        return WaitForWork()


class WaitForWork(BotState):
    texts = ['работать', '/start']

    def process_event(self, event, vk_bot):
        try:
            if event.from_user:
                if event.text in self.texts:
                    vk_bot.send_message('ready')
                elif event.text == '/help':
                    vk.send_message('help')
        except Exception:
            try:
                vk_bot.send_message('error_2')
            except Exception:
                pass

    def get_next_state(self):
        command = ['работать', '/start']
        if vk.checked_on_false_messenge(event.text, *command):
            return WorkState()
        else:
            return WaitForWork()


class WorkState(BotState):

    def process_event(self, event, vk_bot):
        try:
            label = ['/start']
            vk.get_keyboard(label=label)

            commands = ['Я все', 'я все', 'конец', 'хватит', 'стоп', 'Cancel', 'Add link with tag']

            if event.attachments:
                post_url = 'https://vk.com/'\
                           + event.attachments['attach1_type']\
                           + event.attachments['attach1']
                print(post_url)
                try:
                    data = ({'title': '', 'url': post_url, 'uid': event.user_id, 'tags': []})
                    vk_bot.answer(data)
                except Exception as E:
                    print(E)
                    vk_bot.send_message('error_2')

            else:
                if event.text not in commands:
                    try:

                        data = ({'title': '', 'url': event.text, 'uid': event.user_id, 'tags': []})
                        vk_bot.answer(data)
                    except Exception as E:
                        print(E)


                elif event.text == 'Add link with tag':
                    vk_bot.send_message('link_with_tag_saver1')
                else:
                    vk_bot.send_message('end')
        except Exception:
            try:
                vk_bot.send_message('error_2')
            except Exception:
                pass

    def get_next_state(self):

        commands = ['Я все', 'я все', 'конец', 'хватит', 'стоп', 'Cancel']

        if event.text == 'Add link with tag':
            return StateAddTag()
        elif vk.checked_on_false_messenge(event.text, *commands):
            return WaitForWork()
        else:
            return WorkState()


class StateAddTag(BotState):

    def process_event(self, event, vk_bot):
        try:
            label = ['End']
            vk.get_keyboard(label=label)
            if event.text == 'Cancel':
                vk_bot.send_message('return_to_normal')

            elif event.attachments:

                label = ['/start']
                vk.get_keyboard(label=label)

                vk.post = 'https://vk.com/'\
                          + event.attachments['attach1_type']\
                          + event.attachments['attach1']
                vk_bot.send_message('link_with_tag_saver2')

            elif event.text == 'End':
                label = ['/start']
                vk.get_keyboard(label=label)
                vk_bot.vk.messages.send(user_id=event.user_id,
                                        message='Okay, Final',
                                        random_id=get_random_id(), keyboard=vk.keyboard)
            elif event.text:
                vk.post = event.text
                vk_bot.send_message('link_with_tag_saver2')
        except Exception:
            try:
                vk_bot.send_message('error_2')
            except Exception:
                pass

    def get_next_state(self):
        if event.text == 'End':
            return HiState()
        elif event.text == 'Cancel':
            return WorkState()
        else:
            return StateAddLinkWithTag()


class StateAddLinkWithTag(BotState):

    def process_event(self, event, vk_bot):
        try:
            if event.text == 'Cancel':

                label = ['Add link with tag', 'Cancel']
                vk.get_keyboard(label=label)

                vk_bot.send_message('return_to_normal')

            elif event.text:
                try:
                    label = ['/start']
                    vk.get_keyboard(label=label)

                    vk.tags = event.text
                    print(vk.post, vk.tags)

                    data = ({'title': '',
                             'url': vk.post,
                             'uid': event.user_id,
                             'tags': vk.tags.split(' ')
                             })
                    vk_bot.answer(data)
                except Exception as E:
                    print(E)
        except Exception:
            try:
                vk_bot.send_message('error_2')
            except Exception:
                pass

    def get_next_state(self):
        if event.text == 'Cancel':
            return WorkState()
        else:
            return HiState()


"""
запуск основного процесса 
"""
if __name__ == '__main__':
    vk = VKBot()
    for event in vk.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.from_user:
            vk.process_event(event)
