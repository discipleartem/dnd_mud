"""Отрисовка экранов приветствия и главного меню."""

from typing import Any

from colorama import Fore, Style

from ui.input_handler import get_int_input
from ui.window_manager import get_terminal_width, print_header, print_wrapped


def show_welcome_screen(version: str, loc: Any) -> None:
    """Отобразить приветственный экран с ASCII-рамкой и версией.

    Args:
        version: Строка версии (из pyproject.toml)
        loc: Объект локализации
    """
    width = get_terminal_width() - 2
    title = loc('welcome.title')
    subtitle = loc('welcome.subtitle')
    version_text = loc('welcome.version', version=version)

    print()
    print_header(title, width=width, fill_char='=')

    print()
    print_wrapped(subtitle, color=Fore.GREEN, width=width)
    print_wrapped(version_text, color=Fore.CYAN, width=width)
    print()


def show_main_menu(loc: Any) -> int:
    """Отобразить главное меню и получить выбор пользователя.

    Returns:
        Номер выбранного пункта (1-8)
    """
    width = get_terminal_width() - 2
    separator = Fore.YELLOW + '=' * width + Style.RESET_ALL

    # Заголовок
    print_header(loc('menu.caption'), width=width, fill_char='-')
    print()

    # Пункты меню
    menu_items = [
        ('1', loc('menu.new_game')),
        ('2', loc('menu.load_game')),
        ('3', loc('menu.create_character')),
        ('4', loc('menu.settings')),
        ('5', loc('menu.languages')),
        ('6', loc('menu.mods')),
        ('7', loc('menu.adventures')),
        ('8', loc('menu.exit')),
    ]

    for num, label in menu_items:
        print(f'  {Fore.YELLOW}{num}{Style.RESET_ALL}. {label}')

    print()
    print(separator)
    print()

    prompt = loc('menu.prompt', min=1, max=8)
    return get_int_input(prompt, 1, 8, loc)