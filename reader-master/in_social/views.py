"""
Модуль с функциями-обработчиками страниц.
"""
import datetime
import json
import requests
from reader import parser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from in_social.forms import LoginForm, RegistrationForm, ThemeForm,\
    ProfileEditForm, PasswordEditForm, SearchUser, AccountsForm, \
    CreateCanalForm, AddUserToCanal, EditArticleForm, \
    NewPostForm, FilterPostForm, AddImageUser, SearchPostForm, SearchCanalForm
from in_social.tokens import CONFIRM_TOKEN
from in_social.themes import THEMES
from in_social import models


def admin_required(function):
    """
    Декоратор для проверки is_superuser и is_staff.
    :param function: функция
    :return: функция или перенаправление на главную страницу
    """
    def inner(request, *args, **kwargs):
        if request.user.is_superuser and request.user.is_staff:
            return function(request, *args, **kwargs)
        messages.add_message(request, messages.ERROR, "Недостаточно прав.")
        return redirect('/')
    return inner


def get_base_context(request):
    """
    Получение базового контекста.
    :param request: объект запроса
    :return: базовый контекст
    """
    context = dict()
    if request.user.is_authenticated:
        try:
            theme_model = models.ThemeChanger.objects.get(user=request.user)
        except ObjectDoesNotExist:
            theme_model = models.ThemeChanger(
                theme='primary', background_theme='light', user=request.user
            )
            theme_model.save()

        try:
            avatar = models.UserAvatar.objects.get(user=request.user)
            context['avatar'] = avatar.image.url
            context['default_avatar'] = False
        except ObjectDoesNotExist:
            context['avatar'] = '/static/default.jpg'
            context['default_avatar'] = True
        context['theme'] = THEMES[theme_model.theme]
        context['bg_theme'] = theme_model.background_theme
    else:
        context['theme'] = THEMES['primary']
        context['bg_theme'] = 'light'
    context['user'] = request.user
    context['login_form'] = LoginForm()
    return context


def get_base_admin_context():
    """
    Получение базового контекста администратора.
    :return: базовый контекст администратора
    """
    opportunities = [
        dict(name='Управление пользователями', url='/admin/users/')
    ]
    return opportunities


def index_page(request):
    """
    Главная страница сайта.
    :param request: объект запроса
    :return: объект ответа сервера с HTML
    """
    context = get_base_context(request)
    return render(request, 'index.html', context)


def profile_reg_page(request):
    """
    Страница регистрации пользователя.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    :return redirect: перенаправление на главную страницу сайта
    """
    if not request.user.is_authenticated:
        context = get_base_context(request)
        context['reg_form'] = RegistrationForm()
        if request.method == 'POST':
            reg_form = RegistrationForm(request.POST)
            context['reg_form'] = reg_form
            if reg_form.is_valid():
                username = reg_form.data['username']
                password = reg_form.data['password']
                first_name = reg_form.data['first_name']
                last_name = reg_form.data['last_name']
                email = reg_form.data['email']
                if not User.objects.filter(username=username).exists():
                    if not User.objects.filter(email=email).exists():
                        user = User.objects.create_user(username, email, password)
                        user.first_name = first_name
                        user.last_name = last_name
                        user.is_active = False
                        user.save()
                        theme = models.ThemeChanger(
                            theme='primary', background_theme='light', user=user
                        )
                        theme.save()

                        # Аккаунты пользователя в вк и тг
                        user_accounts = models.UserAccounts(user=user, user_vk="", user_tg="")
                        user_accounts.save()

                        current_site = get_current_site(request)
                        mail_subject = 'Активация аккаунта на сайте Reader'
                        message = render_to_string('registration/reg_confirm_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': CONFIRM_TOKEN.make_token(user),
                        })
                        email_message = EmailMessage(
                            mail_subject, message, to=[reg_form.data['email']]
                        )
                        email_message.send()
                        messages.add_message(
                            request, messages.INFO,
                            "Мы отправили Вам письмо с инструкцией для активации аккаунта."
                            " В данный момент доступ к Вашему аккаунту ограничен."
                        )
                        return redirect('/')
                    messages.add_message(request, messages.ERROR,
                                         "Выбранная почта привязана к другому аккаунту.")
                else:
                    messages.add_message(request, messages.ERROR,
                                         "Пользователь с таким логином уже существует.")
            else:
                messages.add_message(request, messages.ERROR,
                                     "Некорректные данные в форме регистрации.")
        return render(request, 'registration/reg.html', context)
    messages.add_message(request, messages.WARNING, "Вы уже зарегистрированы.")
    return redirect('/')


def profile_activate_page(request, uidb64, token):
    """
    Страница подтверждения регистрации профиля.
    :param request: объект запроса
    :param uidb64: закодированный ключ
    :param token: токен
    :return redirect: перенаправление на главную страницу
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and CONFIRM_TOKEN.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.add_message(request, messages.SUCCESS, "Вы успешно зарегистрировались.")
    else:
        messages.add_message(request, messages.ERROR,
                             "Не удалось подтвердить регистрацию аккаунта.")
    return redirect('/')


@login_required
def profile_edit_page(request):
    """
    Страница изменения данных пользователя.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    :return redirect: перенаправление на эту же страницу
    """
    context = get_base_context(request)
    context['edit_form'] = ProfileEditForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    })
    if request.method == 'POST':
        edit_form = ProfileEditForm(request.POST)
        context['edit_form'] = edit_form
        if edit_form.is_valid():
            if request.user.first_name != edit_form.data['first_name'] or \
                    request.user.last_name != edit_form.data['last_name'] or \
                    request.user.email != edit_form.data['email']:
                if not User.objects.filter(email=edit_form.data['email']).exists() or \
                        request.user.email == edit_form.data['email']:
                    request.user.first_name = edit_form.data['first_name']
                    request.user.last_name = edit_form.data['last_name']
                    request.user.save()
                    if request.user.email != edit_form.data['email']:
                        current_site = get_current_site(request)
                        mail_subject = 'Изменение почтового адреса на сайте Reader'
                        message = render_to_string('registration/edit_confirm_email.html', {
                            'user': request.user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                            'token': CONFIRM_TOKEN.make_token(request.user),
                        })
                        email_message = EmailMessage(
                            mail_subject, message, to=[edit_form.data['email']]
                        )
                        email_message.send()
                        edit_email = models.EditEmail(
                            user=request.user, email=edit_form.data['email']
                        )
                        edit_email.save()
                        messages.add_message(request, messages.INFO,
                                             "Мы отправили Вам на почту письмо"
                                             " с инструкциями для изменения E-mail."
                                             " Остальные данные были успешно изменены")
                    else:
                        messages.add_message(request, messages.SUCCESS,
                                             "Вы успешно изменили данные профиля.")
                    return redirect('/profile/')
                messages.add_message(request, messages.ERROR,
                                     "Выбранная почта привязана к другому аккаунту.")
            else:
                messages.add_message(request, messages.WARNING,
                                     "Новые данные профиля совпадают со старыми.")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме.")
    return render(request, 'registration/edit.html', context)


def profile_edit_confirm_page(request, uidb64, token):
    """
    Страница подтверждения изменения E-mail.
    :param request: объект запроса
    :param uidb64: закодированный ключ
    :param token: токен
    :return redirect: перенаправление на страницу редактирования профиля
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, ObjectDoesNotExist):
        user = None
    if user is not None and CONFIRM_TOKEN.check_token(user, token):
        try:
            edit_email = models.EditEmail.objects.get(user=user)
            user.email = edit_email.email
            user.save()
            edit_email.delete()
            messages.add_message(request, messages.SUCCESS, "Вы успешно изменили E-mail.")
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR,
                                 "Не удалось изменить E-mail.")
    else:
        messages.add_message(request, messages.ERROR,
                             "Не удалось изменить E-mail.")
    return redirect('/profile')


@login_required
def change_password_page(request):
    """
    Страница смены пароля пользователя.
    :param request: объект запроса
    :return: объект ответа сервера с HTML
    """
    context = get_base_context(request)
    context['password_edit'] = PasswordEditForm()
    if request.method == 'POST':
        password_edit_form = PasswordEditForm(request.POST)
        if password_edit_form.is_valid():
            old_password = password_edit_form.data['old_password']
            if request.user.check_password(old_password):
                new_password = password_edit_form.data['new_password']
                password_confirmation = password_edit_form.data['password_confirmation']
                if new_password == password_confirmation:
                    if new_password != old_password:
                        request.user.set_password(new_password)
                        request.user.save()
                        update_session_auth_hash(request, request.user)
                        messages.add_message(request, messages.SUCCESS,
                                             "Вы успешно изменили пароль.")
                    else:
                        messages.add_message(request, messages.WARNING,
                                             "Новый пароль совпадает со старым.")
                else:
                    messages.add_message(request, messages.ERROR, "Пароли не совпадают.")
            else:
                messages.add_message(request, messages.ERROR, "Неправильный текущий пароль.")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме смены пароля.")
    return render(request, "registration/password_edit.html", context)


def profile_login_page(request):
    """
    Авторизация пользователя на сайте.
    Не имеет своей страницы.
    :param request: объект запроса
    :return: перенаправление на главную страницу
    """
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.data['username']
            password = login_form.data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, "Авторизация успешна.")
            else:
                try:
                    selected_user = User.objects.get(username=username)
                    if selected_user.is_active:
                        messages.add_message(request, messages.ERROR,
                                             "Неправильный логин или пароль.")
                    else:
                        messages.add_message(request, messages.ERROR,
                                             "Данный пользователь заблокирован.")
                except ObjectDoesNotExist:
                    messages.add_message(request, messages.WARNING,
                                         "Пользователя с таким логином не существует,"
                                         " но вы можете стать им :)")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме авторизации.")
    return redirect('/')


@login_required
def profile_logout_page(request):
    """
    Деавторизация пользователя.
    Не имеет своей страницы.
    :param request: объект запроса
    :return: перенаправление на главную страницу
    """
    logout(request)
    messages.add_message(request, messages.SUCCESS, "Вы успешно вышли из аккаунта")
    return redirect('/')


@login_required
def theme_changer_page(request):
    """
    Страница смены темы сайта.
    Тема привязывается к аккаунту на сайте.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    :return redirect: перенаправление на эту же страницу
    """
    context = get_base_context(request)
    theme = models.ThemeChanger.objects.get(user=request.user)
    context['theme_form'] = ThemeForm(
        initial={'theme': theme.theme, 'bg_theme': theme.background_theme}
    )
    if request.method == 'POST':
        theme_form = ThemeForm(request.POST)
        if theme_form.is_valid():
            theme_changer = models.ThemeChanger.objects.get(user=request.user)
            theme_changer.theme = theme_form.data['theme']
            theme_changer.background_theme = theme_form.data['bg_theme']
            theme_changer.save()
            return redirect('/profile/themes')
    return render(request, 'themes.html', context)


@admin_required
@login_required
def admin_page(request):
    """
    Страница с возможностями для администраторов.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    :return redirect: перенаправление на главную страницу
    """
    context = get_base_context(request)
    context['opportunities'] = get_base_admin_context()
    return render(request, 'admin/admin_page.html', context)


@admin_required
@login_required
def admin_opportunity_users(request):
    """
    Управление пользователями.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    :return redirect: перенаправление на главную страницу
    """
    context = get_base_context(request)
    context['all_users'] = User.objects.all()
    context['search_user'] = SearchUser()
    if request.method == 'POST':
        search_user = SearchUser(request.POST)
        context['search_user'] = search_user
        if search_user.is_valid():
            context['all_users'] = User.objects.filter(username__contains=search_user.data['user'])
    return render(request, 'admin/admin_op_users.html', context)


@admin_required
@login_required
def admin_make_admin(request, user_id):
    """
    Делает пользователя superuser'ом.
    :param request: объект запроса
    :param user_id: ID пользователя
    :return:
    """
    selected_user = User.objects.get(id=user_id)
    selected_user.is_superuser = 1
    selected_user.is_staff = 1
    selected_user.save()
    print(request)
    return redirect('/admin/users')


@admin_required
@login_required
def admin_make_user(request, user_id):
    """
    Понижает до пользователя.
    :param request: объект запроса
    :param user_id: ID пользователя
    :return:
    """
    selected_user = User.objects.get(id=user_id)
    selected_user.is_superuser = 0
    selected_user.is_staff = 0
    selected_user.save()
    print(request)
    return redirect('/admin/users')


@admin_required
@login_required
def block_user(request, user_id):
    """
    Блокирует пользователя.
    :param request: объект запроса
    :param user_id: ID пользователя
    :return redirect: перенаправление на страницу
    """
    selected_user = User.objects.get(id=user_id)
    selected_user.is_active = 0
    selected_user.save()
    print(request)
    return redirect('/admin/users')


@admin_required
@login_required
def unblock_user(request, user_id):
    """
    Разблокирует пользователя.
    :param request: объект запроса
    :param user_id: ID пользователя
    :return redirect: перенаправление на страницу
    """
    selected_user = User.objects.get(id=user_id)
    selected_user.is_active = 1
    selected_user.save()
    print(request)
    return redirect('/admin/users')


@login_required
def canals_page(request):
    """
    Страница с отображением списка каналов и чата.
    :param request: объект запроса
    :return: объект ответа сервера с HTML
    """
    context = get_base_context(request)

    # Получение списка каналов, в которых есть текущий пользователь.
    user_canals = models.UserCanals.objects.filter(user=request.user).order_by('-datetime')
    user_canals_with_last_msg = []
    for user_canal in user_canals:
        msgs_from_canal = models.PostsCanals.objects.filter(canal=user_canal.canal)
        if msgs_from_canal:
            last_msg_from_canal = msgs_from_canal.latest('datetime')
        else:
            last_msg_from_canal = False
        user_canals_with_last_msg.append(
            {'user_canal': user_canal, 'last_msg': last_msg_from_canal}
        )

    context['user_canals'] = user_canals_with_last_msg

    context['canal_form'] = CreateCanalForm()
    context['user_form'] = AddUserToCanal()
    context['search_canal'] = SearchCanalForm()

    # Запрос на выбор канала
    canal_id = request.GET.get("id")
    if canal_id is not None:
        try:
            selected_canal = models.Canals.objects.get(id=canal_id)
            selected_user_canal = user_canals.get(canal=selected_canal, user=request.user)
            context['sel_canal'] = selected_user_canal

            users_in_canal = models.UserCanals.objects.filter(canal=selected_canal)
            users_in_canal_with_avatars = []
            for user_in_canal in users_in_canal:
                try:
                    avatar_of_user = models.UserAvatar.objects.get(
                        user=user_in_canal.user
                    ).image.url
                except ObjectDoesNotExist:
                    avatar_of_user = '/static/default.jpg'

                users_in_canal_with_avatars.append({
                    'user_in_canal': user_in_canal,
                    'avatar_of_user': avatar_of_user
                })
            context['users_and_avatars'] = users_in_canal_with_avatars
            context['count_of_users'] = len(users_in_canal)
            context['count_of_users_mod'] = len(users_in_canal) % 10

            msgs = models.PostsCanals.objects.filter(canal=selected_canal)
            messages_and_avatars = []
            for msg in msgs:
                try:
                    user_avatar = models.UserAvatar.objects.get(user=msg.user).image.url
                except ObjectDoesNotExist:
                    user_avatar = '/static/default.jpg'

                try:
                    models.LikesPostInCanals.objects.get(user=request.user, post=msg)
                    is_liked = True
                except ObjectDoesNotExist:
                    is_liked = False

                post_likes = models.LikesPostInCanals.objects.filter(post=msg).order_by('-datetime')

                users_likes = [post_like.user for post_like in post_likes]
                users_likes_avatars = []
                for user_like in users_likes[:5]:
                    try:
                        user_like_avatar = models.UserAvatar.objects.get(user=user_like).image.url
                        users_likes_avatars.append(user_like_avatar)
                    except ObjectDoesNotExist:
                        users_likes_avatars.append('/static/default.jpg')

                messages_and_avatars.append({
                    'msg': msg,
                    'post_tags': models.PostsTags.objects.filter(post=msg.post),
                    'user_avatar': user_avatar,
                    'is_liked': is_liked,
                    'total_likes': len(post_likes),
                    'avatars_likes': users_likes_avatars
                })
            context['msgs_and_avatars'] = messages_and_avatars

        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'Вы не состоите в этом канале.')
            return redirect('/canals')
    else:
        context['sel_canal'] = False

    # Добавление пользователя в канал
    if request.method == 'POST':
        user_form = AddUserToCanal(request.POST)
        context['user_form'] = user_form
        if user_form.is_valid():
            add_user_to_canal(request, user_form.data['username'], context['sel_canal'])
            return redirect('/canals?id=' + str(context['sel_canal'].canal.id))

    # Создание канала
    if request.method == 'POST':
        canal_form = CreateCanalForm(request.POST)
        context['canal_form'] = canal_form
        if canal_form.is_valid():
            if not models.Canals.objects.filter(
                    name=canal_form.data['canal_name']
            ).exists():
                create_canal(
                    request.user, canal_form.data['canal_name'], canal_form.data['secret_code']
                )
                messages.add_message(request, messages.SUCCESS, 'Вы успешно создали канал.')
            else:
                messages.add_message(request, messages.ERROR,
                                     'Канал с таким названием уже существует.')
            return redirect('/canals')

    # Поиск канала
    if request.method == 'POST':
        search_canal = SearchCanalForm(request.POST)
        context['search_canal'] = search_canal
        if search_canal.is_valid():
            try:
                found_canal = models.Canals.objects.get(name=search_canal.data['search_name'])
                if found_canal.code == search_canal.data['search_code']:
                    if not models.UserCanals.objects.filter(
                            canal=found_canal, user=request.user
                    ).exists():
                        user_canal = models.UserCanals(
                            canal=found_canal, user=request.user, datetime=datetime.datetime.now()
                        )
                        user_canal.save()
                        messages.add_message(request, messages.SUCCESS,
                                             'Вы вошли в канал ' + str(found_canal.name))
                    else:
                        messages.add_message(request, messages.WARNING,
                                             'Вы уже состоите в канале ' + str(found_canal.name))
                else:
                    messages.add_message(request, messages.ERROR, 'Неправильный секретный код.')
            except ObjectDoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'Канал с таким названием не существует.')
            return redirect('/canals')

    return render(request, 'canals.html', context)


def update_datetime(selected_canal):
    """
    Обновляет дату и время у канала.
    :param selected_canal: канал в виде объекта UserCanals
    """
    user_canals = models.UserCanals.objects.filter(canal=selected_canal)
    for user_canal in user_canals:
        user_canal.datetime = datetime.datetime.now()
        user_canal.save()


def create_canal(user, canal_name, secret_code):
    """
    Функция для создания канала.
    :param user: Пользователь
    :param canal_name: Название канала
    :param secret_code: Секретный код-пароль для подключения к каналу
    """
    new_canal = models.Canals(admin=user, name=canal_name, code=secret_code)
    new_canal.save()
    user_canal = models.UserCanals(canal=new_canal, user=user, datetime=datetime.datetime.now())
    user_canal.save()


def exit_from_canal(request, user_canal_id):
    """
    Выход из канала или его удаление.
    :param request: объект запроса
    :param user_canal_id: ID канала, в котором состоит пользователь
    :return: перенаправление на страницу с каналами
    """
    try:
        selected_user_canal = models.UserCanals.objects.get(id=user_canal_id)
        canal_name = selected_user_canal.canal.name
        if request.user == selected_user_canal.canal.admin:
            selected_canal = selected_user_canal.canal
            selected_canal.delete()
            messages.add_message(request, messages.SUCCESS,
                                 'Вы успешно удалили канал ' + str(canal_name))
        else:
            selected_user_canal.delete()
            messages.add_message(request, messages.SUCCESS,
                                 'Вы успешно вышли из канала ' + str(canal_name))
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Вы не состоите в этом канале.')
    return redirect('/canals')


def add_user_to_canal(request, username, selected_canal):
    """
    Добавляет пользователя в канал. Работает с помощью вызова из других функций.
    :param request: объект запроса
    :param username: имя пользователя
    :param selected_canal: канал в виде объекта UserCanals
    """
    try:
        selected_user = User.objects.get(username=username)
        if not models.UserCanals.objects.filter(
                canal=selected_canal.canal, user=selected_user
        ).exists():
            user_canal = models.UserCanals(
                canal=selected_canal.canal, user=selected_user, datetime=datetime.datetime.now()
            )
            user_canal.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Вы добавили пользователя "
                                 + username + " в канал " + selected_canal.canal.name + '.')
            update_datetime(selected_canal.canal)
        else:
            messages.add_message(request, messages.WARNING,
                                 "Пользователь " + username +
                                 " уже состоит в канале " + selected_canal.canal.name + '.')
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR,
                             "Пользователя " + username + " не существует.")


def kick_user_from_canal(request, canal_id, user_id):
    """
    Исключает пользователя из канала. Работает с помощью ссылки.
    :param request: объект запроса
    :param canal_id: ID канала (модель Canals)
    :param user_id: ID пользователя
    :return redirect: перенаправление на выбранный канал
    """
    try:
        selected_user = User.objects.get(id=user_id)
        selected_canal = models.Canals.objects.get(id=canal_id)
        if selected_canal.admin == request.user:
            if request.user != selected_user:
                selected_user_canal = models.UserCanals.objects.get(
                    user=selected_user, canal=selected_canal
                )
                selected_user_canal.delete()
                messages.add_message(request, messages.SUCCESS,
                                     'Вы исключили пользователя ' + selected_user.username +
                                     ' из канала ' + selected_canal.name + '.')
                update_datetime(selected_canal)
            else:
                messages.add_message(request, messages.ERROR,
                                     'Вы не можете исключить из канала себя.')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Вы не являетесь администратором канала '
                                 + selected_canal.name + '.')
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR,
                             'Такого канала или пользователя не существует.')
    return redirect('/canals?id=' + str(canal_id))


@login_required
def articles_of_user(request):
    """
    Страница с отображением всех постов пользователя.
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    """
    context = get_base_context(request)

    # Получение списка каналов для функции "Поделиться"
    user_canals = models.UserCanals.objects.filter(user=request.user).order_by('-datetime')
    context['user_canals'] = user_canals

    context['new_post_form'] = NewPostForm()
    context['search_post'] = SearchPostForm()

    # Получение текущей сортировки
    try:
        post_filter = models.FilterPost.objects.get(user=request.user)
    except ObjectDoesNotExist:
        post_filter = models.FilterPost(user=request.user)
        post_filter.save()

    # Использование полученной сортировки
    if post_filter.post_sort == 'date':
        articles = models.SavedPosts.objects.filter(user=request.user).order_by('-datetime')
    else:
        articles = models.SavedPosts.objects.filter(user=request.user).order_by('title')

    context['post_filter_form'] = FilterPostForm(initial={'post_sort': post_filter.post_sort})

    if request.method == 'POST':

        # Обработка данных для сортировки
        if 'post_sort' in request.POST.keys():
            filter_post_form = FilterPostForm(request.POST)
            if filter_post_form.is_valid():
                post_filter.post_sort = filter_post_form.data['post_sort']
                post_filter.save()
                return redirect('/articles')
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме сортировки")

        # Обработка данных для поиска
        if 'search_title' in request.POST.keys():
            search_post_form = SearchPostForm(request.POST)
            context['search_post'] = search_post_form
            if search_post_form.is_valid():
                articles = articles.filter(
                    title__contains=search_post_form.data['search_title']
                )
                articles = articles.filter(
                    url__contains=search_post_form.data['search_url']
                )
                if search_post_form.data['search_tags'].split():
                    search_tags = search_post_form.data['search_tags'].split()
                    selected_post_tags = []
                    new_articles = []

                    if request.POST.get('type_of_search_tags', False) == 'or':
                        # Поиск по тегам ИЛИ
                        for search_tag in search_tags:
                            selected_post_tags += models.PostsTags.objects.filter(tag=search_tag)
                        articles_from_tags = [
                            selected_post_tag.post for selected_post_tag in selected_post_tags
                        ]
                        new_articles = [
                            article for article in articles if article in articles_from_tags
                        ]
                    else:
                        # Поиск по тегам И
                        for article in articles:
                            article_tags = models.PostsTags.objects.filter(post=article)
                            tags_names = [
                                article_post_tag.tag for article_post_tag in article_tags
                            ]
                            if len(search_tags) <= len(tags_names):
                                if all(search_tag in tags_names for search_tag in search_tags):
                                    new_articles.append(article)

                    articles = new_articles
            else:
                messages.add_message(request, messages.ERROR, "Некорректные данные в форме поиска")

        # Обработка данных для создания статьи
        if 'title' in request.POST.keys():
            new_post_form = NewPostForm(request.POST)
            context['new_post_form'] = new_post_form
            if new_post_form.is_valid():
                saved_post = models.SavedPosts(
                    user=request.user, datetime=datetime.datetime.now(),
                    title=new_post_form.data['title'], url=new_post_form.data['url']
                )
                saved_post.save()
                auto_tags = []
                if request.POST.get('auto_tags', False):
                    try:
                        requests.request("get", new_post_form.data['url'])
                        title, auto_tags = parser.parse(new_post_form.data['url'])
                        print(title)

                    except requests.exceptions.ConnectionError:
                        messages.add_message(
                            request, messages.WARNING,
                            "Мы не смогли проставить теги к вашей статье."
                            " Проверьте правильность ссылки.")
                tags = new_post_form.data['tags'].split() + auto_tags
                for tag in tags:
                    if not check_this_tag_by_name(saved_post, tag):
                        new_post_tag = models.PostsTags(post=saved_post, tag=tag)
                        new_post_tag.save()

                messages.add_message(request, messages.SUCCESS, "Вы успешно добавили статью.")
                return redirect('/articles')
            messages.add_message(request, messages.ERROR,
                                 "Некорректные данные в форме создания статьи.")

    # Создание словаря со статьями и их тегами
    articles_and_tags = []
    for article in articles:
        articles_and_tags.append({
            'article': article, 'tags': models.PostsTags.objects.filter(post=article)
        })
    context['articles'] = articles_and_tags

    return render(request, 'articles.html', context)


@login_required
def share_post(request, user_canal_id, post_id):
    """
    Возможность поделиться постом с каналом.
    :param request: объект запроса
    :param user_canal_id: ID канала
    :param post_id: ID поста
    :return: объект ответа сервера с HTML
    """
    try:
        user_canal = models.UserCanals.objects.get(id=user_canal_id)
        try:
            canal = user_canal.canal
            post = models.SavedPosts.objects.get(id=post_id)
            post_in_canal = models.PostsCanals(
                canal=canal, user=request.user,
                datetime=datetime.datetime.now(), post=post
            )
            post_in_canal.save()
            update_datetime(canal)
            messages.add_message(request, messages.SUCCESS, "Вы успешно поделились статьёй.")
            return redirect('/canals?id=' + str(canal.id))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "Произошла какая-то ошибка")
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Вы не состоите в этом канале.")
    return redirect('/articles')


def load_tags(article):
    """
    Выгружает теги для поста
    :param article: пост, для которого нужно выгрузить тег
    :return: tags
    """
    try:
        tags = models.PostsTags.objects.filter(post=article)
    except ObjectDoesNotExist:
        tags = []
    return tags


def check_this_tag(article, id_tag):
    """
    Проверяет на существование тега с id - id_tag у поста article
    :param article: пост
    :param id_tag: айди тега
    :return: True/False в зависимости от существования тега
    """
    try:
        selected_tag = models.PostsTags.objects.get(id=id_tag)
        if article == selected_tag.post:
            return True
    except ObjectDoesNotExist:
        print('Does not Exist', id_tag)
    return False


def check_this_tag_by_name(article, name_tag):
    """
    Проверяет на существование тега - name_tag у поста article
    :param article: пост
    :param name_tag: тег (строка)
    :return: True/False в зависимости от существования тега
    """
    try:
        models.PostsTags.objects.get(post=article, tag=name_tag)
        return True
    except ObjectDoesNotExist:
        pass
    return False


@login_required
def edit_article(request, article_id):
    """
    Изменяет данные статьи.
    :param request: объект запроса
    :param article_id: ID статьи
    :return: объект ответа сервера с HTML
    """
    context = get_base_context(request)
    try:
        article = models.SavedPosts.objects.get(id=article_id)
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Такой статьи не существует.')
        return redirect('/articles')

    context['edit_article_form'] = EditArticleForm(
        initial={'title': article.title, 'link': article.url}
    )

    context['tags'] = load_tags(article)

    if request.method == 'POST':
        edit_article_form = EditArticleForm(request.POST)
        context['edit_article_form'] = edit_article_form
        if edit_article_form.is_valid():
            article.title = edit_article_form.data['title']
            article.url = edit_article_form.data['link']
            article.datetime = datetime.datetime.now()
            article.save()

            tags = edit_article_form.data['tags']
            # in deleted_tags there are ids of tags
            try:
                deleted_tags = request.POST.getlist('deleted_tags')
                if isinstance(deleted_tags, list):
                    for id_tag in deleted_tags:
                        if check_this_tag(article, id_tag):
                            models.PostsTags.objects.get(id=id_tag).delete()
                else:
                    if check_this_tag(article, deleted_tags):
                        models.PostsTags.objects.get(id=deleted_tags).delete()
            except ObjectDoesNotExist:
                pass

            tags = tags.split()
            for tag in tags:
                if not check_this_tag_by_name(article, tag):
                    new_post_tag = models.PostsTags(post=article, tag=tag)
                    new_post_tag.save()
            messages.add_message(request, messages.SUCCESS, 'Вы успешно изменили статью.')
            return redirect('/articles/')
        messages.add_message(request, messages.ERROR,
                             "Некорректные данные в форме.")
    return render(request, 'edit_article.html', context)


@login_required
def delete_article(request, article_id):
    """
    Удаление статьи
    :param request: объект запроса
    :param article_id: ID статьи
    :return: перенаправление на страницу со статьями
    """
    try:
        article = models.SavedPosts.objects.get(id=article_id)
        article.delete()
        messages.add_message(request, messages.SUCCESS, "Вы успешно удалили статью.")
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Такой статьи не существует.')
    return redirect('/articles')


@login_required
def accounts(request):
    """
    Страница с аккаунтами, привязанными к профилю
    :param request: объект запроса
    :return render: объект ответа сервера с HTML
    """
    context = get_base_context(request)
    # Получение текущих аккаунтов
    try:
        user_accounts = models.UserAccounts.objects.get(user=request.user)
    except ObjectDoesNotExist:
        user_accounts = models.UserAccounts(user=request.user, user_vk="", user_tg="")
        user_accounts.save()

    context['accounts_form'] = AccountsForm(
        initial={'user_vk': user_accounts.user_vk, 'user_tg': user_accounts.user_tg}
    )

    if request.method == 'POST':
        accounts_form = AccountsForm(request.POST)
        context['accounts_form'] = accounts_form
        if accounts_form.is_valid():
            new_user_vk = accounts_form.data["user_vk"]
            new_user_tg = accounts_form.data["user_tg"]

            not_changed = True
            vk_exists = False
            tg_exists = False

            if user_accounts.user_vk != new_user_vk:
                not_changed = False
                if not models.UserAccounts.objects.filter(user_vk=new_user_vk).exists():
                    user_accounts.user_vk = new_user_vk
                elif user_accounts.user_vk != new_user_vk:
                    vk_exists = True

            if user_accounts.user_tg != new_user_tg:
                not_changed = False
                if not models.UserAccounts.objects.filter(user_tg=new_user_tg).exists():
                    user_accounts.user_tg = new_user_tg
                elif user_accounts.user_tg != new_user_tg:
                    tg_exists = True

            if not_changed:
                messages.add_message(request, messages.WARNING,
                                     "Старые данные совпадают с новыми.")
            elif vk_exists and tg_exists:
                messages.add_message(request, messages.ERROR,
                                     'Оба аккаунта уже привязаны к другому профилю.')
            elif vk_exists:
                messages.add_message(request, messages.ERROR,
                                     'Пользователь ВК уже привязан к другому профилю.')
            elif tg_exists:
                messages.add_message(request, messages.ERROR,
                                     'Аккаунт TG уже привязан к другому профилю.')
            else:
                messages.add_message(request, messages.SUCCESS,
                                     'Вы успешно обновили данные аккаунтов')

            user_accounts.save()
            return redirect('/profile/accounts')

    return render(request, "accounts.html", context)


def get_token_api():
    """
    Функция возвращающая token из файла на сервере для выполнения POST-запросов к API
    :return: token
    """
    token_file = open('/var/www/reader/reader/token.txt', 'r')
    return token_file.readline()


def api(request):
    """
    Функция для добавления поста в базу данных
    :param request: объект запроса
    POST:
    - params: (dict) должен включать в себя:
    uid: айди юзера
    title: заголовок сохранёнки
    url: ссылка
    tags: теги
    who_is: отправка производиться ботом Вк/TG (значения: vk/tg)
    - token: ключ аутентификации
    :return 0
    """
    if request.method == "POST":
        data = json.loads(request.POST.get('json'))
        token = data['token']
        if len(data['params']) == 5:
            uid = data['params']['uid']
            title = data['params']['title']
            url = data['params']['url']
            tags = data['params']['tags']
            who_is = data['params']['who_is']
        else:
            messages.add_message(request, messages.ERROR,
                                 "Что с твоими параметрами, чел?")
            return HttpResponse(status=400)
    else:
        messages.add_message(request, messages.ERROR,
                             "Братан, мы туда только POST-запросом пускаем")
        return HttpResponse(status=400)

    if token != get_token_api():
        messages.add_message(request, messages.ERROR,
                             "Dude, у тебя неправильный токен")
        return HttpResponse(status=403)

    if who_is == "vk":
        try:
            uid = models.UserAccounts.objects.get(user_vk=uid).id
        except ObjectDoesNotExist:
            return HttpResponse(status=404)
    if who_is == "tg":
        try:
            uid = models.UserAccounts.objects.get(user_tg=uid).id
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

    user = User.objects.get(id=uid)
    date = datetime.datetime.now()
    post = models.SavedPosts(user=user, title=title, url=url, datetime=date)
    post.save()
    if tags:
        if isinstance(tags, list):
            for current_tag in tags:
                tag = models.PostsTags(tag=current_tag, post=post)
                tag.save()
        else:
            tag = models.PostsTags(tag=tags, post=post)
            tag.save()
    return HttpResponse(status=200)


@login_required
def upload_avatar(request):
    """
    Страница загрузки аватара для пользователя.
    :param request: объект запроса
    :return redirect: перенаправление на эту же страницу
    :return render: объект ответа сервера с HTML
    """
    context = get_base_context(request)
    context['avatar_form'] = AddImageUser()
    if request.method == 'POST':
        avatar_form = AddImageUser(request.POST, request.FILES)
        context['avatar_form'] = avatar_form
        if avatar_form.is_valid() and avatar_form.check_content():
            if avatar_form.check_size():
                if avatar_form.check_resolution():
                    try:
                        old_avatar = models.UserAvatar.objects.get(user=request.user)
                        old_avatar.image.delete()
                        avatar = models.UserAvatar(image=request.FILES['image'], user=request.user)
                        avatar.save()
                    except ObjectDoesNotExist:
                        avatar = models.UserAvatar(image=request.FILES['image'], user=request.user)
                        avatar.save()
                    messages.add_message(request, messages.SUCCESS,
                                         'Вы успешно установили изображение профиля.')
                    return redirect('/profile/avatar/')
                messages.add_message(request, messages.WARNING,
                                     'Разрешение изображения не должно превышать 1600x1600')
            else:
                messages.add_message(request, messages.WARNING,
                                     'Размер изображения не должен превышать 2 МБ')
        else:
            messages.add_message(request, messages.ERROR,
                                 'Неправильный тип файла. Используйте jpeg или png.')

    return render(request, 'avatar.html', context)


@login_required
def remove_avatar(request):
    """
    Страница удаления аватара у пользователя.
    :param request: объект запроса
    :return redirect: перенаправление на другую страницу
    """
    try:
        avatar = models.UserAvatar.objects.get(user=request.user)
        avatar.image.delete()
        avatar.delete()
        messages.add_message(request, messages.SUCCESS, 'Вы успешно удалили аватар')
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Неверно введен ID')
    return redirect('/profile/avatar/')


@login_required
def like_to_canal_post(request, canal_post_id):
    """
    Поставить лайк на пост или удалить лайк с поста.
    :param request: объект запроса
    :param canal_post_id: ID поста в канале
    :return: перенаправление на другую страницу
    """
    try:
        canal_post = models.PostsCanals.objects.get(id=canal_post_id)
        canal = canal_post.canal
        try:
            # Проверка на то, что пользователь лайкает пост, который он видит.
            models.UserCanals.objects.get(user=request.user, canal=canal)
            try:
                # Удаление лайка, если лайк был
                like_post = models.LikesPostInCanals.objects.get(user=request.user, post=canal_post)
                like_post.delete()
            except ObjectDoesNotExist:
                # Создание лайка, если лайка ещё не было
                like_post = models.LikesPostInCanals(
                    user=request.user, post=canal_post, datetime=datetime.datetime.now()
                )
                like_post.save()
            return redirect('/canals?id=' + str(canal.id))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, 'Данный пост Вам не доступен.')
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'Такого поста не существует.')
    return redirect('/canals')
