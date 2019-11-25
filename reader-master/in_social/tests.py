"""
Модуль тестов для сайта.
"""

import datetime
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from in_social import models
from in_social.views import update_datetime, create_canal, add_user_to_canal,\
    load_tags, check_this_tag_by_name, check_this_tag


class AnonPagesTest(TestCase):
    """
    Класс с тестами для анонимного пользователя.
    """
    def setUp(self):
        """
        Метод подготовки данных для тестов
        """
        self.client = Client()

    def test_index_page(self):
        """
        Проверка на работоспособность главной страницы.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_reg_page(self):
        """
        Проверка на работоспособность страницы регистрации.
        """
        response = self.client.get('/profile/reg/')
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page(self):
        """
        Тест на доступность страницы восстановления пароля.
        """
        response = self.client.get('/reset-password/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page(self):
        """
        Тест на запретную страницу для пользователя.
        Ожидается перенаправление на главную страницу.
        """
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/profile/')

    def test_anon_context(self):
        """
        Проверка контекста при анонимном пользователе.
        """
        response = self.client.get('/')
        self.assertEqual('#4a76a8', response.context['theme'].base_color)
        self.assertEqual('#3a6899', response.context['theme'].secondary_color)
        self.assertEqual('light', response.context['bg_theme'])


class UserPagesTest(TestCase):
    """
    Класс с тестами для настоящего пользователя.
    """
    def setUp(self):
        """
        Метод подготовки данных для тестов
        """
        self.user = User.objects.create_user(
            username='vladimir', email='vladimir@mail.ru', password='keklol123'
        )
        self.user.save()
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(user=self.user)

    def test_reg_page(self):
        """
        Проверка на работоспособность страницы регистрации.
        Должно быть перенаправление на главную страницу.
        """
        response = self.client.get('/profile/reg/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_logout(self):
        """
        Тест на выход из аккаунта.
        """
        response = self.client.get('/profile/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/?next=/profile/')

    def test_canals_page(self):
        """
        Тест на работоспособность страницы с каналами
        """
        response = self.client.get('/canals/')
        self.assertEqual(response.status_code, 200)

    def test_articles_page(self):
        """
        Тест на работоспособность страницы со статьями.
        """
        response = self.client.get('/articles/')
        self.assertEqual(response.status_code, 200)

    def test_article_create_and_edit(self):
        """
        Тест на проверку работоспособности страницы редактирования статьи после создания статьи.
        """
        current_datetime = datetime.datetime.now()
        new_article = models.SavedPosts(
            title='Крутой заголовок',
            url='https://wow.ru/kek',
            datetime=current_datetime,
            user=self.user
        )
        new_article.save()
        existing_article = models.SavedPosts.objects.get(
            user=self.user,
            datetime=current_datetime,
            title='Крутой заголовок',
            url='https://wow.ru/kek'
        )
        response = self.client.get('/articles/edit/' + str(existing_article.id))
        self.assertEqual(response.status_code, 200)

    def test_themes_page(self):
        """
        Проверка на работоспособность страницы тем.
        """
        response = self.client.get('/profile/themes/')
        self.assertEqual(response.status_code, 200)

    def test_accounts_page(self):
        """
        Тест на работоспособность страницы с аккаунтами.
        Предварительно должны быть созданы специальные модели.
        """
        user_accounts = models.UserAccounts(user=self.user, user_vk="", user_tg="")
        user_accounts.save()
        response = self.client.get('/profile/accounts/')
        self.assertEqual(response.status_code, 200)

    def test_user_context(self):
        """
        Проверка контекста при обычном пользователе.
        """
        response = self.client.get('/')
        self.assertEqual('#4a76a8', response.context['theme'].base_color)
        self.assertEqual('#3a6899', response.context['theme'].secondary_color)
        self.assertEqual('light', response.context['bg_theme'])
        theme_model = models.ThemeChanger.objects.get(user=self.user)
        theme_model.theme = 'green'
        theme_model.background_theme = 'dark'
        theme_model.save()
        response = self.client.get('/')
        self.assertEqual('#156b39', response.context['theme'].base_color)
        self.assertEqual('#146636', response.context['theme'].secondary_color)
        self.assertEqual('dark', response.context['bg_theme'])


class SpecialFunctionsTest(TestCase):
    """
    Класс с тестами для одиночных функций, используемых на страницах.
    """
    def setUp(self):
        """
        Метод подготовки данных для тестов
        """
        self.user = User.objects.create_user(
            username='vladimir', email='vladimir@mail.ru', password='keklol123'
        )
        self.user.save()
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(user=self.user)

    def test_create_canal(self):
        """
        Проверка функции, создающей канал.
        """

        create_canal(self.user, 'Canal Name', 'Secret 123')
        try:
            models.Canals.objects.get(name='Canal Name', code='Secret 123')
            created_canal = True
        except ObjectDoesNotExist:
            created_canal = False
        self.assertTrue(created_canal)

    def test_add_user(self):
        """
        Проверка функции, добавляющей пользователя в канал.
        """
        create_canal(self.user, 'Canal Name', 'Secret 123')
        response = self.client.get('/canals/')

        another_user = User.objects.create_user(
            username='kek', email='kek@mail.ru', password='kekkek123'
        )
        another_user.save()
        existing_canal = models.Canals.objects.get(name='Canal Name', code='Secret 123')
        existing_user_canal = models.UserCanals.objects.get(
            canal=existing_canal, user=self.user
        )
        add_user_to_canal(response.wsgi_request, 'kek', existing_user_canal)
        try:
            models.UserCanals.objects.get(canal=existing_canal, user=another_user)
            is_user_in_canal = True
        except ObjectDoesNotExist:
            is_user_in_canal = False
        self.assertTrue(is_user_in_canal)

    def test_update_canal_time(self):
        """
        Проверка функции, обновляющей время в канале
        """
        create_canal(self.user, 'Canal Name', 'Secret 123')
        existing_canal = models.Canals.objects.get(name='Canal Name', code='Secret 123')
        old_datetime = models.UserCanals.objects.get(
            canal=existing_canal, user=self.user
        ).datetime
        update_datetime(existing_canal)
        new_datetime = models.UserCanals.objects.get(
            canal=existing_canal, user=self.user
        ).datetime
        self.assertNotEqual(old_datetime, new_datetime)

    def test_get_tags(self):
        """
        Проверка функции, возвращающей теги
        """
        article = models.SavedPosts(
            user=self.user,
            datetime=datetime.datetime.now(),
            title='Kek article',
            url='https://kek.ru'
        )
        article.save()
        tag1 = models.PostsTags(post=article, tag='wow')
        tag1.save()
        tag2 = models.PostsTags(post=article, tag='amazing')
        tag2.save()
        tags = [tag.tag for tag in load_tags(article)]
        self.assertEqual(['wow', 'amazing'], tags)

    def test_check_tag(self):
        """
        Тестирование для проверки на существование тега по ID.
        """
        article1 = models.SavedPosts(
            user=self.user,
            datetime=datetime.datetime.now(),
            title='Kek article',
            url='https://kek.ru'
        )
        article1.save()
        article2 = models.SavedPosts(
            user=self.user,
            datetime=datetime.datetime.now(),
            title='Kek article',
            url='https://kek.ru'
        )
        article2.save()
        tag1 = models.PostsTags(post=article1, tag='wow')
        tag1.save()
        tag2 = models.PostsTags(post=article2, tag='wow')
        tag2.save()
        existing_tag1 = models.PostsTags.objects.get(post=article1, tag='wow')
        existing_tag2 = models.PostsTags.objects.get(post=article2, tag='wow')
        self.assertTrue(check_this_tag(article1, existing_tag1.id))
        self.assertFalse(check_this_tag(article1, existing_tag2.id))

    def test_check_tag_name(self):
        """
        Тестирование функции для проверки на существование тега по имени.
        """
        article = models.SavedPosts(
            user=self.user,
            datetime=datetime.datetime.now(),
            title='Kek article',
            url='https://kek.ru'
        )
        article.save()
        tag1 = models.PostsTags(post=article, tag='wow')
        tag1.save()
        self.assertTrue(check_this_tag_by_name(article, 'wow'))
        self.assertFalse(check_this_tag_by_name(article, 'cool'))


class AdminPagesTest(TestCase):
    """
    Класс с тестами для администратора.
    """
    def setUp(self):
        """
        Метод подготовки данных для тестов
        """
        self.user = User.objects.create_user(
            username='vladimir', email='vladimir@mail.ru', password='keklol123'
        )
        self.user.save()
        self.admin = User.objects.create_user(
            username='admin', email='admin@mail.ru',
            password='admin123', is_staff=True, is_superuser=True
        )
        self.admin.save()
        self.client = Client(enforce_csrf_checks=True)

    def test_admin_page(self):
        """
        Проверка главной страницы администрации.
        """
        self.client.force_login(user=self.user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.client.force_login(user=self.admin)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_admin_users_page(self):
        """
        Проверка админской страницы для отображения пользователей
        """
        self.client.force_login(user=self.user)
        response = self.client.get('/admin/users/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.client.force_login(user=self.admin)
        response = self.client.get('/admin/users/')
        self.assertEqual(response.status_code, 200)
