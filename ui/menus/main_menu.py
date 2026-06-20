"""Приветствие, главное меню и заглушка загрузки игры."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _press_enter, _print_screen_header


def show_welcome_screen(version: str, strings: dict[str, Any]) -> None:
    """Показать приветственный экран."""
    print()
    _print_screen_header(get_string(strings, "welcome.title"))
    print(
        f"{Fore.GREEN}{get_string(strings, 'welcome.subtitle')}"
        f"{Style.RESET_ALL}"
    )
    print(
        f"{Fore.CYAN}"
        f"{get_string(strings, 'welcome.version', version=version)}"
        f"{Style.RESET_ALL}"
    )
    print()


def show_main_menu(strings: dict[str, Any]) -> int:
    """Показать главное меню и получить выбор."""
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'menu.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(f"{Fore.YELLOW}{'-' * 78}{Style.RESET_ALL}")
    print()

    menu_items = [
        ("1", get_string(strings, "menu.new_game")),
        ("2", get_string(strings, "menu.load_game")),
        ("3", get_string(strings, "menu.create_character")),
        ("4", get_string(strings, "menu.settings")),
        ("5", get_string(strings, "menu.languages")),
        ("0", get_string(strings, "menu.exit")),
    ]
    for num, label in menu_items:
        print(f"  {Fore.YELLOW}{num}{Style.RESET_ALL}. {label}")

    print()
    print(SEPARATOR)
    print()

    prompt = get_string(strings, "menu.prompt", max=5)
    return _deps.get_int_input(prompt, 0, 5, strings)


def show_load_game_flow(strings: dict[str, Any]) -> None:
    """Flow «Загрузить игру»."""
    _print_screen_header(get_string(strings, "load_game.caption"))
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'errors.load_not_implemented')}"
        f"{Style.RESET_ALL}"
    )
    print()
    _press_enter(strings)
