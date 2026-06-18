"""Точка входа в игру dnd_mud.

Загружает настройки и строки интерфейса, показывает приветствие
и запускает цикл главного меню.
"""

import sys

from colorama import Fore, Style, init

from core.localization import get_string, load_strings
from core.settings import load_settings, save_settings
from ui.menus import (
    show_main_menu,
    show_settings,
    show_welcome_screen,
    show_new_game_flow,
    show_load_game_flow,
    show_create_character_flow,
    show_languages_menu,
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

        if choice == 0:
            print(
                f"{Fore.GREEN}{get_string(strings, 'info.goodbye')}"
                f"{Style.RESET_ALL}"
            )
            running = False

        elif choice == 1:
            # Новая игра
            show_new_game_flow(strings, settings)

        elif choice == 2:
            # Загрузить игру
            show_load_game_flow(strings)

        elif choice == 3:
            # Создать персонажа
            show_create_character_flow(strings, settings)

        elif choice == 4:
            # Настройки
            new_settings = show_settings(strings, settings)
            # Сохраняем изменения
            save_settings(
                language=new_settings.get("language", settings["language"]),
                hardcore=new_settings.get("hardcore", settings["hardcore"]),
                difficulty=new_settings.get("difficulty", settings.get("difficulty", "normal")),
            )
            settings = new_settings
            # Перезагружаем строки, если язык мог измениться
            strings = load_strings(settings["language"])

        elif choice == 5:
            # Languages
            new_settings = show_languages_menu(strings, settings)
            settings = new_settings
            save_settings(
                language=settings.get("language", "ru"),
                hardcore=settings.get("hardcore", False),
                difficulty=settings.get("difficulty", "normal"),
            )
            strings = load_strings(settings["language"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
