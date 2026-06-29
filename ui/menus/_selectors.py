"""Общие селекторы расы, класса и подкласса."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _print_screen_header
from ui.menus._display import (
    _print_class_info,
    _print_class_summary,
    _print_race_info,
    _print_subclass_info,
)


def select_subrace(
    strings: StringsDict, race_id: str, language: str = "ru"
) -> tuple[bool, str | None]:
    """Показать описание расы и выбрать подрасу."""
    race_full = _deps.load_race_full(race_id, language)
    subraces = race_full.get("subraces", {})
    if not isinstance(subraces, dict) or not subraces:
        return False, None

    if len(subraces) == 1:
        return True, next(iter(subraces))

    _print_screen_header(get_string(strings, "character.subrace_caption"))

    race_name = race_full.get("name", race_id)
    print(f"{Fore.CYAN}{race_name}{Style.RESET_ALL}")
    desc = race_full.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))
    print()

    print(get_string(strings, "character.subraces_label"))
    choices: list[tuple[str, dict[str, Any]]] = []
    for subrace_id, subrace_info in subraces.items():
        if isinstance(subrace_info, dict):
            choices.append((str(subrace_id), subrace_info))

    for idx, (_subrace_id, subrace_info) in enumerate(choices, 1):
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{subrace_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        _print_race_info(subrace_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.subrace_prompt"),
        0,
        len(choices),
        strings,
    )
    if choice == 0:
        return False, None

    subrace_id, _ = choices[choice - 1]
    return True, subrace_id


def select_class(
    strings: StringsDict, language: str = "ru"
) -> dict[str, Any] | None:
    """Выбрать класс персонажа (краткий обзор каждого класса)."""
    classes = _deps.load_classes(language)
    _print_screen_header(get_string(strings, "character.class_caption"))

    class_details: list[dict[str, Any]] = []
    for cls in classes:
        class_id = str(cls.get("id") or cls.get("name"))
        class_details.append(_deps.load_class_full(class_id, language))

    for idx, class_info in enumerate(class_details, 1):
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{'─' * 74}{Style.RESET_ALL}")
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{Style.BRIGHT}"
            f"{class_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        _print_class_summary(class_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.class_prompt"),
        0,
        len(class_details),
        strings,
    )
    if choice == 0:
        return None
    return class_details[choice - 1]


def select_subclass(
    strings: StringsDict,
    class_id: str,
    language: str = "ru",
) -> str | None:
    """Выбрать подкласс (подробный обзор архетипов)."""
    class_full = _deps.load_class_full(class_id, language)
    subclasses = _deps.load_subclasses(class_id, language)

    if not subclasses:
        return None

    _print_screen_header(get_string(strings, "character.subclass_caption"))

    class_label = class_full.get("name", class_id)
    print(f"{Fore.CYAN}{Style.BRIGHT}{class_label}{Style.RESET_ALL}")
    _print_class_info(class_full, strings)
    print()
    print(SEPARATOR)
    print()

    subclasses_title = get_string(
        strings, "character.subclasses_label"
    ).strip()
    print(f"{Fore.YELLOW}{Style.BRIGHT}{subclasses_title}{Style.RESET_ALL}")
    for idx, sub_info in enumerate(subclasses, 1):
        print()
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{'─' * 74}{Style.RESET_ALL}")
            print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{Style.BRIGHT}"
            f"{sub_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        _print_subclass_info(sub_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.subclass_prompt"),
        0,
        len(subclasses),
        strings,
    )
    if choice == 0:
        return None

    selected = subclasses[choice - 1]
    return str(selected.get("id", ""))
