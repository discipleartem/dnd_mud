"""Получение подкласса у наставника (меню персонажей и сценарии)."""

from colorama import Fore, Style

from core.classes import get_subclass_choice_level
from core.localization import get_string
from core.models import Character
from core.types import LanguageCode, StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _print_success_and_wait
from ui.menus.character_flow import _select_subclass


def assign_subclass_from_menu(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
) -> Character | None:
    """Выбрать подкласс и сохранить. None — отмена."""
    subclass_id = _select_subclass(strings, character.class_name, language)
    if subclass_id is None:
        return None

    character.subclass_id = subclass_id
    _deps.update_character(character)
    return character


def run_subclass_trainer(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character | None:
    """Экран выбора подкласса у наставника. None — отмена или без изменений."""
    if character.subclass_id is not None:
        msg = get_string(strings, "characters_menu.subclass_trainer_already")
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
        print()
        return character

    choice_level = get_subclass_choice_level(character.class_name)
    if character.level < choice_level:
        msg = get_string(
            strings,
            "characters_menu.subclass_trainer_level_required",
            level=choice_level,
        )
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
        print()
        return character

    _print_screen_header(
        get_string(strings, "characters_menu.subclass_trainer_caption")
    )

    updated = assign_subclass_from_menu(strings, character, language)
    if updated is None:
        return None

    subclass_id = updated.subclass_id
    name = subclass_id or ""
    for sub in _deps.load_subclasses(character.class_name, language):
        if sub.get("id") == subclass_id:
            name = str(sub.get("name", subclass_id))
            break

    msg = get_string(
        strings, "characters_menu.subclass_trainer_success", name=name
    )
    _print_success_and_wait(strings, msg)
    return updated
