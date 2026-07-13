"""Приветствие, главное меню и заглушка загрузки игры."""

from colorama import Fore, Style

from core.localization import get_string
from core.types import StringsDict
from ui.menus._common import (
    SEPARATOR,
    _print_screen_header,
    _run_numbered_menu,
)


def show_welcome_screen(version: str, strings: StringsDict) -> None:
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


def show_main_menu(strings: StringsDict) -> int:
    """Показать главное меню и получить выбор."""
    print(SEPARATOR)
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, 'menu.caption').center(78)}"
        f"{Style.RESET_ALL}"
    )
    print(SEPARATOR)
    print()

    options = [
        get_string(strings, "menu.new_game"),
        get_string(strings, "menu.load_game"),
        get_string(strings, "menu.characters"),
        get_string(strings, "menu.settings"),
        get_string(strings, "menu.languages"),
        get_string(strings, "menu.mods"),
    ]

    def _separator_before_back() -> None:
        print()
        print(SEPARATOR)

    choice = _run_numbered_menu(
        strings,
        options,
        prompt_key="menu.prompt",
        back_label_key="menu.exit",
        prompt_kwargs={"max": 6},
        before_back=_separator_before_back,
    )
    if choice is None:
        return 0
    return choice
