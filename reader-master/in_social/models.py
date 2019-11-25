"""
Модели для корректной работы сайта и БД.
"""

from django.db import models
from django.contrib.auth.models import User


THEMES = [
    ('primary', 'Стандартный цвет'),
    ('blue', 'Голубой'),
    ('green', 'Зеленый'),
    ('red', 'Карминный'),
    ('indigo', 'Индиго'),
    ('aqua', 'Бирюзовый'),
    ('orange', 'Оранжевый'),
    ('claret', 'Бордовый')
]

BG_THEMES = [
    ('light', 'Светлая'),
    ('dark', 'Тёмная')
]

POST_SORTS = [
    ('name', 'По названию'),
    ('date', 'По дате')
]


class ThemeChanger(models.Model):
    """
    Модель для темы сайта компонентов.
    Имеет два параметра:
    1) главная тема
    2) тема фона
    3) пользователь, использующий тему
    """
    theme = models.CharField(
        max_length=20,
        default='primary',
        choices=THEMES
    )
    background_theme = models.CharField(
        max_length=20,
        default='light',
        choices=BG_THEMES
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )


class Canals(models.Model):
    """
    Модель канала для взаимодействия между пользователями.
    Имеет три поля:
    1) Администратор/создатель канала
    2) Название канала
    3) Секретный код для входа в канал без приглашения
    """
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)


class UserCanals(models.Model):
    """
    Модель, связывающая Canals и User.
    Имеет три поля:
    1) Канал
    2) Время и дата изменений в канале
    3) Пользователь
    """
    canal = models.ForeignKey(Canals, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Link(models.Model):
    """
    Модель ссылки на статью.
    Имеет два поля:
    1) Тема статьи
    2) Ссылка
    """
    theme = models.CharField(max_length=50)
    link = models.TextField()


class SavedPosts(models.Model):
    """
    Личные сохранённые записи пользователей
    user: Пользователь;
    datetime: Время создания записи;
    title: Заголовок;
    url: Ссылка;
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    title = models.CharField(max_length=512, default='')
    url = models.CharField(max_length=512)


class PostsTags(models.Model):
    """
    Модель тэгов для постов.
    Имеет два поля:
    1) Пост, к которому привязан тэг.
    2) Название тэга
    """
    post = models.ForeignKey(SavedPosts, on_delete=models.CASCADE)
    tag = models.CharField(max_length=256)


class PostsCanals(models.Model):
    """
    Модель для хранения статьи в канале.
    Имеет четыре поля:
    1) Канал
    2) Пользователь, создавший сообщение
    3) Время и дата создания сообщения
    4) Пост
    """
    canal = models.ForeignKey(Canals, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    post = models.ForeignKey(SavedPosts, on_delete=models.CASCADE)


class UserAccounts(models.Model):
    """
    Модель с аккаунтами пользователя в различных соцсетях
    user_tg: id-пользователя Telegram
    user_vk: id-пользователя VK
    user: пользователь
    """
    user_tg = models.CharField(max_length=512)
    user_vk = models.CharField(max_length=512)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class FilterPost(models.Model):
    """
    Небольшая моделька для сохранения сортировки статей.
    """
    post_sort = models.CharField(
        max_length=20,
        default='date',
        choices=POST_SORTS
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )


class EditEmail(models.Model):
    """
    Модель для изменения почтового адреса.
    Изменение происходит с помощью подтверждения по почте.
    Имеет 2 поля:
    1) Пользователь
    2) Почта
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    email = models.EmailField(
        max_length=40
    )


class UserAvatar(models.Model):
    """
    Аватарка для пользователя.
    Имеет два поля:
    1) Пользователь
    2) Аватарка (модель ImageField)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to='avatars')


class LikesPostInCanals(models.Model):
    """
    Лайки для поста.
    Имеет три поля;
    1) Пост, получивший лайк
    2) Пользователь, поставивший лайк
    3) Дата лайка
    """
    post = models.ForeignKey(PostsCanals, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
