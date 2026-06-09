"""Точка входа в игру dnd_mud.

Инициализация colorama, загрузка настроек и локализации,
отображение приветствия и главного меню.
"""

import sys

from colorama import Fore, Style, init

from core.localization import Localization
from ui.input_handler import get_int_input
from ui.menus import show_main_menu, show_welcome_screen
from ui.window_manager import print_wrapped

# Версия игры (синхронизирована с pyproject.toml)
VERSION = '0.1.0'

# Настройки по умолчанию
DEFAULT_LANGUAGE = 'ru'


def load_settings() -> dict[str, str | bool]:
    """Загрузить настройки из database/settings.yaml.

    Returns:
        Словарь с настройками
    """
    import yaml

    try:
        with open('database/settings.yaml', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            return {
                'language': data.get('language', DEFAULT_LANGUAGE),
                'font_size': data.get('font_size', 'medium'),
                'hardcore': data.get('hardcore', False),
            }
    except FileNotFoundError:
        return {
            'language': DEFAULT_LANGUAGE,
            'font_size': 'medium',
            'hardcore': False,
        }


def save_settings(settings: dict[str, str | bool]) -> None:
    """Сохранить настройки в database/settings.yaml.

    Args:
        settings: Словарь с настройками
    """
    import yaml

    with open('database/settings.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(settings, f, allow_unicode=True, default_flow_style=False)


def handle_menu_choice(choice: int, loc: Localization) -> bool:
    """Обработать выбор пункта главного меню.

    Args:
        choice: Номер пункта (1-8)
        loc: Объект локализации

    Returns:
        True если нужно продолжить, False если выход
    """
    if choice == 8:
        print_wrapped(loc('info.goodbye'), color=Fore.GREEN)
        return False

    # Все остальные пункты — заглушка
    print_wrapped(loc('errors.not_implemented'), color=Fore.YELLOW)
    input(f'{Fore.CYAN}[Нажмите Enter, чтобы продолжить...]{Style.RESET_ALL}')
    return True


def main() -> int:
    """Главная функция запуска игры.

    Returns:
        0 при успешном завершении
    """
    # Инициализация colorama
    init(autoreset=True)

    # Загрузка настроек
    settings = load_settings()
    language: str = settings.get('language', DEFAULT_LANGUAGE)  # type: ignore

    # Инициализация локализации
    loc = Localization(language)

    # Приветственный экран
    show_welcome_screen(VERSION, loc)

    # Цикл главного меню
    running = True
    while running:
        choice = show_main_menu(loc)
        running = handle_menu_choice(choice, loc)

    return 0


if __name__ == '__main__':
    sys.exit(main())