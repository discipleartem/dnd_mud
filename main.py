"""Точка входа в игру dnd_mud.

Загружает настройки и строки интерфейса, показывает приветствие
и запускает цикл главного меню.
"""

import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from colorama import Fore, Style, init

from core.localization import get_string, load_strings
from core.settings import load_settings, save_settings
from ui.menus import (
    show_create_character_flow,
    show_languages_menu,
    show_load_game_flow,
    show_main_menu,
    show_new_game_flow,
    show_settings,
    show_welcome_screen,
)

_PROJECT_ROOT = Path(__file__).resolve().parent


def _read_version_from_pyproject() -> str:
    """Версия из pyproject.toml — для запуска без pip install -e."""
    with open(_PROJECT_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    ver = project.get("version")
    if isinstance(ver, str):
        return ver
    return "0.0.0"


def _resolve_app_version() -> str:
    """Версия из metadata пакета или fallback на pyproject.toml."""
    try:
        return version("dnd_mud")
    except PackageNotFoundError:
        return _read_version_from_pyproject()


VERSION = _resolve_app_version()


def _save_and_reload_settings(
    settings: dict[str, Any], strings: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Сохранить настройки и перезагрузить строки.

    Args:
        settings: Текущие настройки
        strings: Текущие строки интерфейса

    Returns:
        Кортеж (обновлённые_настройки, обновлённые_строки)
    """
    save_settings(language=settings.get("language", "ru"))
    strings = load_strings(settings["language"])
    return settings, strings


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
            settings, strings = _save_and_reload_settings(settings, strings)

        elif choice == 2:
            # Загрузить игру
            show_load_game_flow(strings)

        elif choice == 3:
            # Создать персонажа
            show_create_character_flow(strings, settings.get("language", "ru"))
            settings, strings = _save_and_reload_settings(settings, strings)

        elif choice == 4:
            # Настройки
            settings = show_settings(strings, settings)
            settings, strings = _save_and_reload_settings(settings, strings)

        elif choice == 5:
            # Languages
            settings = show_languages_menu(strings, settings)
            settings, strings = _save_and_reload_settings(settings, strings)

    return 0


if __name__ == "__main__":
    sys.exit(main())
