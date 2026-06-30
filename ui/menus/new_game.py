"""Flow «Новая игра»: выбор персонажа и приключения."""

from typing import Literal

from colorama import Fore, Style

from core.difficulty import adventure_unavailable_reason
from core.localization import get_string
from core.models import Adventure, Character
from core.types import RuntimeSettings, StringsDict
from ui.menus import _creation_steps, _deps
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _run_numbered_menu,
)
from ui.menus._corrupt_saves import show_corrupt_save_warnings_if_any
from ui.menus._display import _print_characters_list
from ui.menus.scenario_flow import run_scenario

SelectCharacterResult = Character | Literal["create"] | None


def _select_character(
    strings: StringsDict,
    characters: list[Character],
    language: str = "ru",
) -> SelectCharacterResult:
    """Экран выбора персонажа из списка сохранённых."""
    _print_screen_header(get_string(strings, "choose_character.caption"))
    _print_characters_list(strings, characters, language)

    char_count = len(characters)
    create_idx = char_count + 1
    enter_hint = get_string(strings, "common.press_enter")
    print()
    print(
        f"  {Fore.GREEN}{get_string(strings, 'choose_character.create_new')}"
        f" {Fore.LIGHTBLACK_EX}{enter_hint}{Style.RESET_ALL}"
    )
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {Fore.LIGHTBLACK_EX}{get_string(strings, 'choose_character.back')}"
        f"{Style.RESET_ALL}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "choose_character.prompt", count=char_count),
        0,
        create_idx,
        strings,
        default=create_idx,
    )

    if choice == 0:
        return None
    if choice == create_idx:
        return "create"

    return characters[choice - 1]


def _select_adventure(
    strings: StringsDict,
    language: str,
    character: Character,
) -> Adventure | None:
    """Экран выбора приключения с учётом сложности персонажа."""
    adventures: list[Adventure] = _deps.load_adventures()

    if not adventures:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.no_adventures')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return None

    matching: list[Adventure] = []
    other: list[tuple[Adventure, str]] = []
    for adv in adventures:
        reason = adventure_unavailable_reason(adv, character)
        if reason is None:
            matching.append(adv)
        else:
            other.append((adv, reason))

    if not matching:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.none_available')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return None

    def _print_unavailable() -> None:
        if not other:
            return
        print()
        print(
            f"{Fore.LIGHTBLACK_EX}"
            f"{get_string(strings, 'adventures.unavailable_header')}"
            f"{Style.RESET_ALL}"
        )
        for adv, reason_key in other:
            assert reason_key is not None
            reason = get_string(
                strings,
                reason_key,
                min_level=adv.min_level,
            )
            line = get_string(
                strings,
                "adventures.unavailable_line",
                name=adv.get_name(language),
                difficulty=adv.difficulty,
                desc=adv.description,
                reason=reason,
            )
            print(f"  {Fore.LIGHTBLACK_EX}— {line}{Style.RESET_ALL}")

    options = [
        get_string(
            strings,
            "adventures.adventure_line",
            name=adv.get_name(language),
            difficulty=adv.difficulty,
            desc=adv.description,
        )
        for adv in matching
    ]

    _print_screen_header(get_string(strings, "adventures.caption"))

    choice = _run_numbered_menu(
        strings,
        options,
        prompt_key="adventures.prompt",
        back_label_key="adventures.back",
        before_back=_print_unavailable,
    )

    if choice is None:
        return None

    return matching[choice - 1]


def show_new_game_flow(
    strings: StringsDict, settings: RuntimeSettings
) -> None:
    """Flow «Новая игра»: персонаж → приключение."""
    language = settings["language"]
    corrupt_warning_shown = False

    while True:
        characters = _deps.load_characters()
        corrupt_warning_shown = show_corrupt_save_warnings_if_any(
            strings, already_shown=corrupt_warning_shown
        )
        if not characters:
            character = _creation_steps.show_create_character_flow(
                strings, language
            )
        else:
            result = _select_character(strings, characters, language)
            if result is None:
                return
            if result == "create":
                character = _creation_steps.show_create_character_flow(
                    strings, language
                )
            else:
                character = result

        if character is None:
            return

        while True:
            adventure = _select_adventure(strings, language, character)
            if adventure is None:
                break

            character = run_scenario(adventure, character, strings, language)
            return
