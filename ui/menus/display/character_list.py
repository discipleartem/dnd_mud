"""Список персонажей в меню выбора."""

from colorama import Fore, Style

from core.character.models import Character
from core.platform.localization import get_string
from core.types import StringsDict
from ui.menus.display.character_card import _print_character_card


def _print_characters_list(
    strings: StringsDict,
    characters: list[Character],
    language: str,
) -> None:
    """Вывести список сохранённых персонажей."""
    print(
        f"  {Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'choose_character.list_header')}"
        f"{Style.RESET_ALL}"
    )
    print()
    for idx, char in enumerate(characters, 1):
        _print_character_card(idx, char, strings, language)
