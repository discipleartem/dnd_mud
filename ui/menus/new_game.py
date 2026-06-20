"""Flow «Новая игра»: выбор персонажа и приключения."""

from typing import Any, Literal

from colorama import Fore, Style

from core.difficulty import adventure_allows_difficulty
from core.localization import get_string
from core.models import Adventure, Character
from ui.menus import _deps, character_flow
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _run_numbered_menu,
)
from ui.menus._display import _print_character_card

SelectCharacterResult = Character | Literal["create"] | None


def _select_character(
    strings: dict[str, Any], language: str = "ru"
) -> SelectCharacterResult:
    """Экран выбора персонажа из списка сохранённых."""
    characters = _deps.load_characters()

    _print_screen_header(get_string(strings, "choose_character.caption"))
    print(
        f"  {Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'choose_character.list_header')}"
        f"{Style.RESET_ALL}"
    )
    print()

    for idx, char in enumerate(characters, 1):
        _print_character_card(idx, char, strings, language)

    create_idx = len(characters) + 1
    enter_hint = get_string(strings, "common.press_enter")
    print()
    print(
        f"  {Fore.YELLOW}{create_idx}{Style.RESET_ALL}."
        f" {Fore.GREEN}{get_string(strings, 'choose_character.create_new')}"
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
        get_string(strings, "choose_character.prompt", count=create_idx),
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
    strings: dict[str, Any],
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

    matching = [
        adv
        for adv in adventures
        if adventure_allows_difficulty(adv, character.difficulty)
    ]
    other = [
        adv
        for adv in adventures
        if not adventure_allows_difficulty(adv, character.difficulty)
    ]

    if not matching:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'adventures.none_for_difficulty')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return None

    _print_screen_header(get_string(strings, "adventures.caption"))

    for idx, adv in enumerate(matching, 1):
        line = get_string(
            strings,
            "adventures.adventure_line",
            name=adv.get_name(language),
            difficulty=adv.difficulty,
            desc=adv.description,
        )
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {line}")

    if other:
        print()
        print(
            f"{Fore.LIGHTBLACK_EX}"
            f"{get_string(strings, 'adventures.unavailable_header')}"
            f"{Style.RESET_ALL}"
        )
        for adv in other:
            line = get_string(
                strings,
                "adventures.unavailable_line",
                name=adv.get_name(language),
                difficulty=adv.difficulty,
                desc=adv.description,
            )
            print(f"  {Fore.LIGHTBLACK_EX}— {line}{Style.RESET_ALL}")

    choice = _run_numbered_menu(
        strings,
        [],
        prompt_key="adventures.prompt",
        back_label_key="adventures.back",
        prompt_kwargs={"count": len(matching)},
    )

    if choice is None:
        return None

    return matching[choice - 1]


def show_new_game_flow(
    strings: dict[str, Any], settings: dict[str, Any]
) -> None:
    """Flow «Новая игра»: персонаж → приключение."""
    language = settings.get("language", "ru")

    while True:
        characters = _deps.load_characters()
        if not characters:
            character = character_flow.show_create_character_flow(
                strings, language
            )
        else:
            result = _select_character(strings, language)
            if result is None:
                return
            if result == "create":
                character = character_flow.show_create_character_flow(
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

            print()
            launch_msg = get_string(
                strings,
                "new_game.launch",
                adventure=adventure.get_name(language),
                name=character.name,
                difficulty=character.difficulty,
            )
            print(f"{Fore.GREEN}{launch_msg}{Style.RESET_ALL}")
            print()
            _press_enter(strings)
            return
