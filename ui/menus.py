"""Отрисовка экранов меню (приветствие, главное меню, настройки)."""

import os

from colorama import Fore, Style

from ui.input_handler import get_choice, get_int_input
from core.localization import get_string


SEPARATOR = f"{Fore.YELLOW}{'=' * 78}{Style.RESET_ALL}"


def show_welcome_screen(version: str, strings: dict) -> None:
    """Показать приветственный экран.

    Args:
        version: Версия игры
        strings: Словарь со строками интерфейса
    """
    print()
    print(SEPARATOR)
    print(f"{Fore.YELLOW}{get_string(strings, 'welcome.title').center(78)}{Style.RESET_ALL}")
    print(SEPARATOR)
    print()
    print(f"{Fore.GREEN}{get_string(strings, 'welcome.subtitle')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{get_string(strings, 'welcome.version', version=version)}{Style.RESET_ALL}")
    print()


def _clear_screen() -> None:
    """Очистить экран терминала."""
    os.system("cls" if os.name == "nt" else "clear")


def show_main_menu(strings: dict) -> int:
    """Показать главное меню и получить выбор.

    Args:
        strings: Словарь со строками интерфейса

    Returns:
        Номер выбранного пункта (1-2)
    """
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{get_string(strings, 'menu.caption').center(78)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print()

    menu_items = [
        ("1", get_string(strings, "menu.settings")),
        ("2", get_string(strings, "menu.exit")),
    ]
    for num, label in menu_items:
        print(f"  {Fore.YELLOW}{num}{Style.RESET_ALL}. {label}")

    print()
    print(SEPARATOR)
    print()

    prompt = get_string(strings, "menu.prompt", min=1, max=2)
    return get_int_input(prompt, 1, 2)


def show_settings(strings: dict, settings: dict) -> dict:
    """Экран настроек.

    Позволяет переключить режим Hard Core.

    Args:
        strings: Словарь со строками интерфейса
        settings: Текущие настройки {"language": str, "hardcore": bool}

    Returns:
        Обновлённый словарь настроек
    """
    _clear_screen()

    while True:
        print(SEPARATOR)
        print(f"{Fore.YELLOW}{get_string(strings, 'settings.caption').center(78)}{Style.RESET_ALL}")
        print(SEPARATOR)
        print()

        hardcore = settings.get("hardcore", False)
        print(f'  {get_string(strings, "settings.hardcore")}: {hardcore}')
        print()

        # Показываем опции: переключить Hard Core, Назад
        choice = get_choice([
            get_string(strings, "settings.settings_option_hardcore"),
            get_string(strings, "settings.settings_option_back"),
        ], get_string(strings, "settings.prompt", count=2))

        if choice == 2:  # Назад
            break

        if choice == 1:  # Переключить Hard Core
            _clear_screen()
            print(SEPARATOR)
            print(f"{Fore.YELLOW}{get_string(strings, 'settings.hardcore').center(78)}{Style.RESET_ALL}")
            print(SEPARATOR)
            print()

            hc_choice = get_choice([
                get_string(strings, "settings.hardcore_options.off"),
                get_string(strings, "settings.hardcore_options.on"),
            ], get_string(strings, "settings.hardcore_prompt", count=2))

            settings["hardcore"] = (hc_choice == 2)
            print(f"{Fore.GREEN}{get_string(strings, 'settings.hardcore_changed', value=str(settings['hardcore']))}{Style.RESET_ALL}")
            print()
            input(f"{Fore.CYAN}[Enter]{Style.RESET_ALL}")

        _clear_screen()

    return settings