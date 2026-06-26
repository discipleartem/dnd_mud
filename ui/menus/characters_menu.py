"""Меню «Персонажи»: список, создание и удаление."""

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.subclasses import needs_subclass_npc
from core.types import LanguageCode, StringsDict
from ui.menus import _deps, character_flow
from ui.menus._common import (
    _confirm_yes_no,
    _print_cancelled,
    _print_screen_header,
    _print_success_and_wait,
    _run_numbered_menu,
)
from ui.menus._display import _print_characters_list
from ui.menus.subclass_trainer import run_subclass_trainer


def _select_character_for_trainer(
    strings: StringsDict,
    characters: list[Character],
    language: LanguageCode,
) -> Character | None:
    """Выбор персонажа, которому нужен наставник по подклассу."""
    needing = [c for c in characters if needs_subclass_npc(c)]
    if not needing:
        return None

    _print_screen_header(
        get_string(strings, "characters_menu.subclass_trainer_caption")
    )
    _print_characters_list(strings, needing, language)
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
            count=len(needing),
        ),
        0,
        len(needing),
        strings,
    )
    if choice == 0:
        return None
    return needing[choice - 1]


def _run_subclass_trainer_menu(
    strings: StringsDict,
    characters: list[Character],
    language: LanguageCode,
) -> None:
    """Пункт меню: получить подкласс у наставника."""
    character = _select_character_for_trainer(strings, characters, language)
    if character is None:
        return
    run_subclass_trainer(strings, character, language)


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
            if any(needs_subclass_npc(c) for c in characters):
                options.append(
                    get_string(strings, "characters_menu.subclass_trainer")
                )
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
        idx = option_create + 1
        option_trainer: int | None = None
        if has_characters and any(needs_subclass_npc(c) for c in characters):
            option_trainer = idx
            idx += 1
        option_delete_one = idx if has_characters else None
        option_delete_all = idx + 1 if has_characters else None

        if choice == option_create:
            character_flow.show_create_character_flow(strings, language)
            continue

        if option_trainer is not None and choice == option_trainer:
            _run_subclass_trainer_menu(strings, characters, language)
            continue

        if has_characters and choice == option_delete_one:
            _delete_one_character(strings, characters, language)
            continue

        if has_characters and choice == option_delete_all:
            _delete_all_characters(strings, len(characters))
