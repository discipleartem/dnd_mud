"""Точка входа в игру dnd_mud.

Загружает настройки и строки интерфейса, показывает приветствие
и запускает цикл главного меню.
"""

import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from colorama import Fore, Style, init

from core.character.creation_draft import has_creation_draft
from core.platform.catalog_session import get_catalog_session
from core.platform.localization import get_string, load_strings
from core.platform.settings import load_settings, save_settings
from core.types import RuntimeSettings, StringsDict
from ui.input_handler import print_ctrl_c_ignored
from ui.menus import (
    show_characters_menu,
    show_languages_menu,
    show_load_game_flow,
    show_main_menu,
    show_mods_menu,
    show_new_game_flow,
    show_settings,
    show_welcome_screen,
)
from ui.menus.creation.steps import show_continue_character_flow

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
    settings: RuntimeSettings, strings: StringsDict
) -> tuple[RuntimeSettings, StringsDict]:
    """Сохранить настройки и перезагрузить строки.

    Args:
        settings: Текущие настройки
        strings: Текущие строки интерфейса

    Returns:
        Кортеж (обновлённые_настройки, обновлённые_строки)
    """
    save_settings(language=settings["language"])
    strings = load_strings(settings["language"])
    return settings, strings


def _after_hub_menu_action(
    settings: RuntimeSettings, strings: StringsDict
) -> tuple[RuntimeSettings, StringsDict]:
    """Сохранить настройки и перезагрузить строки после hub-действия."""
    return _save_and_reload_settings(settings, strings)


def main() -> int:
    """Запустить игру.

    Returns:
        0 при успешном завершении
    """
    # Инициализация цветного вывода в терминале
    init(autoreset=True)

    # Загружаем настройки
    settings = load_settings()

    get_catalog_session().set_difficulty("normal")

    # Загружаем строки интерфейса на выбранном языке
    strings = load_strings(settings["language"])

    # Показываем приветствие
    show_welcome_screen(VERSION, strings)

    # Главный цикл меню
    running = True
    while running:
        try:
            action = show_main_menu(
                strings, has_creation_draft=has_creation_draft()
            )

            match action:
                case "exit":
                    print(
                        f"{Fore.GREEN}{get_string(strings, 'info.goodbye')}"
                        f"{Style.RESET_ALL}"
                    )
                    running = False
                case "continue":
                    show_continue_character_flow(strings, settings["language"])
                    settings, strings = _after_hub_menu_action(
                        settings, strings
                    )
                case "new_game":
                    show_new_game_flow(strings, settings)
                    settings, strings = _after_hub_menu_action(
                        settings, strings
                    )
                case "load_game":
                    show_load_game_flow(strings, settings["language"])
                case "characters":
                    show_characters_menu(strings, settings["language"])
                    settings, strings = _after_hub_menu_action(
                        settings, strings
                    )
                case "settings":
                    settings = show_settings(strings, settings)
                    settings, strings = _after_hub_menu_action(
                        settings, strings
                    )
                case "languages":
                    settings = show_languages_menu(strings, settings)
                    settings, strings = _after_hub_menu_action(
                        settings, strings
                    )
                case "mods":
                    show_mods_menu(strings, settings["language"])
        except KeyboardInterrupt:
            print()
            print_ctrl_c_ignored(strings)

    return 0


if __name__ == "__main__":
    sys.exit(main())
