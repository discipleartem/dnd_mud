"""Точка входа в игру dnd_mud.

Загружает настройки и строки интерфейса, показывает приветствие
и запускает цикл главного меню.
"""

import sys

from colorama import Fore, Style, init

from core.localization import load_strings, get_string
from core.settings import load_settings, save_settings
from ui.menus import (
    show_welcome_screen,
    show_main_menu,
    show_settings,
)

# Версия игры
VERSION = "0.1.0"


def main() -> int:
    """Запустить игру.

    Returns:
        0 при успешном завершении
    """
    # Инициализация цветного вывода в терминале
    init(autoreset=True)

    # Загружаем настройки
    settings = load_settings()

    # Загружаем строки интерфейса на выбранном языке
    strings = load_strings(settings["language"])

    # Показываем приветствие
    show_welcome_screen(VERSION, strings)

    # Главный цикл меню
    running = True
    while running:
        choice = show_main_menu(strings)

        if choice == 2:
            print(f"{Fore.GREEN}{get_string(strings, 'info.goodbye')}{Style.RESET_ALL}")
            running = False

        elif choice == 1:
            # Настройки
            new_settings = show_settings(strings, settings)
            # Сохраняем изменения
            save_settings(
                language=new_settings.get("language", settings["language"]),
                hardcore=new_settings.get("hardcore", settings["hardcore"]),
            )
            settings = new_settings
            # Перезагружаем строки, если язык мог измениться
            strings = load_strings(settings["language"])

    return 0


if __name__ == "__main__":
    sys.exit(main())