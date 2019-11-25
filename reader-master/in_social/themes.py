"""
Темы для сайта, привязанные к аккаунту пользователя.
"""


class Theme(object):
    """
    Шаблон для остальных тем.
    """
    base_color = None
    secondary_color = None


class DefaultTheme(Theme):
    """
    Дефолтная тема голубоватого цвета.
    Да, я взял её у ВК.
    """
    base_color = "#4a76a8"
    secondary_color = "#3a6899"


class BlueTheme(Theme):
    """
    Голубая тема на замену дефолтной.
    """
    base_color = "#2261a1"
    secondary_color = "#205c99"


class GreenTheme(Theme):
    """
    Зелёная тема.
    Словно густой лес в ясную погоду.
    """
    base_color = '#156b39'
    secondary_color = '#146636'


class RedTheme(Theme):
    """
    Тема кирпичного цвета.
    Такая же надежная, как и сам кирпич.
    """
    base_color = '#900c3e'
    secondary_color = '#890b3b'


class IndigoTheme(Theme):
    """
    Тема цвета индиго.
    На языке простых смертных - фиолетовая.
    """
    base_color = '#6c3483'
    secondary_color = '#67317c'


class AquaTheme(Theme):
    """
    Бирюзовая тема.
    Успокаивает агрессивных пользователей.
    """
    base_color = '#148f77'
    secondary_color = '#138b73'


class OrangeTheme(Theme):
    """
    Оранжевая тема.
    Оттенки оранжевого - мои кошмары.
    Этот вроде выглядит неплохо.
    """
    base_color = '#af601a'
    secondary_color = '#a65b19'


class ClaretTheme(Theme):
    """
    Бордовая тема.
    """
    base_color = '#922b21'
    secondary_color = '#8d2a20'


THEMES = {
    'primary': DefaultTheme(),
    'blue': BlueTheme(),
    'green': GreenTheme(),
    'red': RedTheme(),
    'indigo': IndigoTheme(),
    'aqua': AquaTheme(),
    'orange': OrangeTheme(),
    'claret': ClaretTheme()
}
