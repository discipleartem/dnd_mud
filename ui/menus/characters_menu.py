"""Меню «Персонажи»: список, создание и удаление."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from ui.menus import _deps, character_flow
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _run_numbered_menu,
)
from ui.menus._display import _print_character_card


def _confirm(strings: dict[str, Any], prompt_key: str, **kwargs: Any) -> bool:
    """Подтвердить действие: 1 — да, 0 — нет."""
    choice = _deps.get_int_input(
        get_string(strings, prompt_key, **kwargs),
        0,
        1,
        strings,
    )
    return choice == 1


def _print_characters_list(
    strings: dict[str, Any],
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


def _select_character_to_delete(
    strings: dict[str, Any],
    characters: list[Character],
    language: str,
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
    strings: dict[str, Any],
    characters: list[Character],
    language: str,
) -> None:
    """Удалить одного персонажа с подтверждением."""
    character = _select_character_to_delete(strings, characters, language)
    if character is None:
        return

    if not _confirm(
        strings,
        "characters_menu.confirm_delete_one",
        name=character.name,
    ):
        print(
            f"{Fore.LIGHTBLACK_EX}"
            f"{get_string(strings, 'characters_menu.cancelled')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    if character.save_slug:
        _deps.delete_character(character.save_slug)

    msg = get_string(
        strings,
        "characters_menu.delete_success",
        name=character.name,
    )
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
    print()
    _press_enter(strings)


def _delete_all_characters(strings: dict[str, Any], count: int) -> None:
    """Удалить всех персонажей с подтверждением."""
    if not _confirm(
        strings,
        "characters_menu.confirm_delete_all",
        count=count,
    ):
        print(
            f"{Fore.LIGHTBLACK_EX}"
            f"{get_string(strings, 'characters_menu.cancelled')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    deleted = _deps.delete_all_characters()
    msg = get_string(
        strings,
        "characters_menu.delete_all_success",
        count=deleted,
    )
    print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
    print()
    _press_enter(strings)


def show_characters_menu(strings: dict[str, Any], language: str = "ru") -> None:
    """Меню управления персонажами: список, создание, удаление."""
    while True:
        characters = _deps.load_characters()
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

        if choice == 1:
            character_flow.show_create_character_flow(strings, language)
            continue

        if has_characters and choice == 2:
            _delete_one_character(strings, characters, language)
            continue

        if has_characters and choice == 3:
            _delete_all_characters(strings, len(characters))
