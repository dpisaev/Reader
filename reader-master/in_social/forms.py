"""
Формы для получения входных данных.
"""
from django import forms
from django.core.files.images import get_image_dimensions
from in_social.models import THEMES, BG_THEMES, POST_SORTS


SEARCH_TAGS_TYPE = [
    ('and', 'И'),
    ('or', 'Или')
]


class LoginForm(forms.Form):
    """
    Форма авторизации пользователя.
    """
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Логин: ',
            }
        )
    )
    password = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Пароль: ',
            }
        )
    )


class RegistrationForm(forms.Form):
    """
    Форма регистрации пользователя.
    """
    first_name = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Фамилия'
    )
    email = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='E-mail'
    )
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Логин'
    )
    password = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Пароль'
    )


class ProfileEditForm(forms.Form):
    """
    Форма редактирования основных данных профиля пользователя.
    """
    first_name = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Имя'
    )
    last_name = forms.CharField(
        max_length=40,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Фамилия'
    )
    email = forms.CharField(
        max_length=40,
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='E-mail'
    )


class PasswordEditForm(forms.Form):
    """
    Форма смены пароля пользователя.
    """
    old_password = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Текущий пароль'
    )

    new_password = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Новый пароль'
    )

    password_confirmation = forms.CharField(
        max_length=20,
        min_length=3,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Новый пароль ещё раз'
    )


class ThemeForm(forms.Form):
    """
    Форма выбора темы сайта.
    """
    bg_theme = forms.ChoiceField(
        label='Основная тема',
        choices=BG_THEMES,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    theme = forms.ChoiceField(
        label='Цвет компонентов',
        choices=THEMES,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )


class SearchUser(forms.Form):
    """
    Форма поиска пользователя.
    """
    user = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Никнейм',
                'style': 'border-top-left-radius: 0.25rem; border-bottom-left-radius: 0.25rem;'
            }
        ),
        required=False
    )


class CreateCanalForm(forms.Form):
    """
    Форма создания канала.
    """
    canal_name = forms.CharField(
        label='Название канала:',
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    secret_code = forms.CharField(
        label='Секретный код:',
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


class AccountsForm(forms.Form):
    """
    Форма смены/подключения аккаунтов вк, телеграм
    """
    user_vk = forms.CharField(
        max_length=40,
        min_length=1,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Ваш id ВК'
    )

    user_tg = forms.CharField(
        max_length=40,
        min_length=1,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Ваш id Telegram'
    )


class AddUserToCanal(forms.Form):
    """
    Форма добавления пользователя в канал.
    """
    username = forms.CharField(
        label='Имя пользователя: ',
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


class EditArticleForm(forms.Form):
    """
    Форма редактирования статьи.
    """
    title = forms.CharField(
        label='Название: ',
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    link = forms.URLField(
        label='Ссылка: ',
        max_length=512,
        required=True,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    tags = forms.CharField(
        label='Теги: ',
        max_length=256,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Добавление нового тега'

            }
        )
    )


class AddImageUser(forms.Form):
    """
    Форма добавления изображения пользователем.
    """
    image = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'custom-file-input'
            }
        )
    )

    def check_resolution(self):
        """
        Проверяет разрешение изображения.
        :return True: если разрешение меньше 800x800
        :return False: если разрешение больше 800x800
        """
        image = self.cleaned_data['image']
        width, height = get_image_dimensions(image)
        if width > 1600 or height > 1600:
            return False
        return True

    def check_size(self):
        """
        Проверяет размер изображения.
        :return True: если размер меньше 200 КБ
        :return False: если размер больше 200 КБ
        """
        image = self.cleaned_data['image']
        print(len(image))
        if len(image) > 2* 1024 * 1024:
            return False
        return True

    def check_content(self):
        """
        Проверяет тип изображения.
        :return True: если png или jpeg
        :return False: если любой другой тип
        """
        image = self.cleaned_data['image']
        main, sub = image.content_type.split('/')
        print(main, sub)
        if main == 'image' and (sub in ['jpeg', 'png']):
            return True
        return False


class NewPostForm(forms.Form):
    """
    Форма для создания нового поста.
    """
    title = forms.CharField(
        label='Заголовок: ',
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    url = forms.URLField(
        label='Ссылка: ',
        max_length=512,
        required=True,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    tags = forms.CharField(
        label='Теги: ',
        max_length=256,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Например: cool tags cats dogs'
            }
        )
    )


class FilterPostForm(forms.Form):
    """
    Форма сортировки постов.
    """
    post_sort = forms.ChoiceField(
        label='Сортировка',
        choices=POST_SORTS,
        widget=forms.Select(
            attrs={
                'class': 'form-control text-center',
                'id': 'post_filter'
            }
        )
    )


class SearchPostForm(forms.Form):
    """
    Форма поиска статей.
    """
    search_title = forms.CharField(
        max_length=512,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Заголовок',
        required=False
    )

    search_url = forms.CharField(
        max_length=512,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Ссылка',
        required=False
    )

    search_tags = forms.CharField(
        max_length=512,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Теги',
        required=False
    )

    type_of_search_tags = forms.ChoiceField(
        label='Вариант поиска тегов: ',
        choices=SEARCH_TAGS_TYPE,
        widget=forms.Select(
            attrs={
                'class': 'form-control text-center w-25'
            }
        )
    )


class SearchCanalForm(forms.Form):
    """
    Форма поиска канала
    """
    search_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Название'
    )
    search_code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
        label='Секретный код',
        required=False
    )
