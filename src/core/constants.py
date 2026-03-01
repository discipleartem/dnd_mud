"""Общие константы проекта.

Следует принципам:
- DRY: Единственное место для всех строковых констант
- KISS: Простые и понятные названия
"""

# Приветственные сообщения и интерфейс
WELCOME_MESSAGE = "Добро пожаловать в D&D Text MUD!"
PRESS_ENTER = "Нажмите Enter для продолжения..."
GOODBYE_MESSAGE = "До свидания!"

# Меню
MAIN_MENU_TITLE = "D&D Text MUD"
MENU_ITEMS = ["Новая игра", "Загрузить игру", "Настройки", "Выход"]
MENU_PROMPT = "Ваш выбор: "

# Сообщения
NOT_AVAILABLE = "Функция пока недоступна."
THANKS_FOR_PLAYING = "Спасибо за игру!"
CHARACTER_CREATED = "Персонаж {name} создан!"
CHARACTER_NAME_PROMPT = "Введите имя персонажа: "
ERROR_EMPTY_NAME = "Имя не может быть пустым"
ERROR_CREATING_CHARACTER = "Ошибка создания персонажа: {error}"

# Цвета для консоли (если доступны)
COLOR_CYAN = "cyan"
COLOR_GREEN = "green"
COLOR_RED = "red"
COLOR_WHITE = "white"

# Разделитель
SEPARATOR_LENGTH = 50
SEPARATOR_CHAR = "="
