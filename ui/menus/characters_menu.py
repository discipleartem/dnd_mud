"""Меню «Персонажи»: список, создание и удаление."""

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.types import LanguageCode, StringsDict
from ui.menus import _creation_steps, _deps
from ui.menus._common import (
    _confirm_yes_no,
    _print_cancelled,
    _print_screen_header,
    _print_success_and_wait,
    _run_numbered_menu,
)
from ui.menus._corrupt_saves import show_corrupt_save_warnings_if_any
from ui.menus._display import _print_characters_list


def _select_character_to_delete(
    strings: StringsDict,
    characters: list[Character],
    language: LanguageCode,
) -> Character | None:
    """Выбор персонажа для удаления."""
    _print_screen_header(get_string(strings, "characters_menu.caption"))
    _print_characters_list(strings, characters, language)
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'characters_menu.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(
            strings,
            "characters_menu.select_prompt",
            count=len(characters),
        ),
        0,
        len(characters),
        strings,
    )
    if choice == 0:
        return None
    return characters[choice - 1]


def _delete_one_character(
    strings: StringsDict,
    characters: list[Character],
    language: LanguageCode,
) -> None:
    """Удалить одного персонажа с подтверждением."""
    character = _select_character_to_delete(strings, characters, language)
    if character is None:
        return

    if not _confirm_yes_no(
        strings,
        "characters_menu.confirm_delete_one",
        name=character.name,
    ):
        _print_cancelled(strings)
        return

    if character.save_slug:
        _deps.delete_character(character.save_slug)

    msg = get_string(
        strings,
        "characters_menu.delete_success",
        name=character.name,
    )
    _print_success_and_wait(strings, msg)


def _delete_all_characters(strings: StringsDict, count: int) -> None:
    """Удалить всех персонажей с подтверждением."""
    if not _confirm_yes_no(
        strings,
        "characters_menu.confirm_delete_all",
        count=count,
    ):
        _print_cancelled(strings)
        return

    deleted = _deps.delete_all_characters()
    msg = get_string(
        strings,
        "characters_menu.delete_all_success",
        count=deleted,
    )
    _print_success_and_wait(strings, msg)


def show_characters_menu(
    strings: StringsDict, language: LanguageCode = "ru"
) -> None:
    """Меню управления персонажами: список, создание, удаление."""
    load_result = None
    corrupt_warning_shown = False
    while True:
        if load_result is None:
            load_result = _deps.load_characters()
            corrupt_warning_shown = show_corrupt_save_warnings_if_any(
                strings,
                corrupt_labels=load_result.corrupt_save_warnings,
                already_shown=corrupt_warning_shown,
            )
        characters = list(load_result.characters)
        has_characters = bool(characters)

        _print_screen_header(get_string(strings, "characters_menu.caption"))

        if has_characters:
            _print_characters_list(strings, characters, language)
        else:
            print(
                f"  {Fore.LIGHTBLACK_EX}"
                f"{get_string(strings, 'characters_menu.empty_list')}"
                f"{Style.RESET_ALL}"
            )

        print()
        options = [get_string(strings, "characters_menu.create")]
        if has_characters:
            options.append(get_string(strings, "characters_menu.delete_one"))
            options.append(get_string(strings, "characters_menu.delete_all"))

        choice = _run_numbered_menu(
            strings,
            options,
            prompt_key="characters_menu.prompt",
            back_label_key="characters_menu.back",
        )
        if choice is None:
            return

        option_create = 1
        option_delete_one = 2 if has_characters else None
        option_delete_all = 3 if has_characters else None

        if choice == option_create:
            _creation_steps.show_create_character_flow(strings, language)
            load_result = None
            continue

        if has_characters and choice == option_delete_one:
            _delete_one_character(strings, characters, language)
            load_result = None
            continue

        if has_characters and choice == option_delete_all:
            _delete_all_characters(strings, len(characters))
            load_result = None
