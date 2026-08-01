"""Выбор предыстории при создании персонажа."""

from typing import Any

from colorama import Fore, Style

from core.catalogs.backgrounds import (
    get_background_skills,
    load_background_full,
    load_backgrounds,
)
from core.platform.localization import get_string
from core.types import StringsDict
from ui.menus.console import print_screen_header, read_numbered_choice
from ui.menus.display import _print_background_info


def select_creation_background(
    strings: StringsDict,
    language: str = "ru",
) -> tuple[str, list[str]] | None:
    """Выбор предыстории; (id, навыки) или None. Языки — на следующем шаге."""
    backgrounds = load_backgrounds(language)
    print_screen_header(get_string(strings, "character.background_caption"))

    details: list[dict[str, Any]] = []
    for bg in backgrounds:
        bg_id = str(bg.get("id", ""))
        details.append(load_background_full(bg_id, language))

    for idx, bg in enumerate(details, 1):
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{'─' * 74}{Style.RESET_ALL}")
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{Style.BRIGHT}{bg.get('name', '?')}{Style.RESET_ALL}"
        )
        _print_background_info(bg, strings, language)

    print()
    choice = read_numbered_choice(
        strings,
        len(details),
        prompt_key="character.background_prompt",
    )
    if choice is None:
        return None

    selected = details[choice - 1]
    background_id = str(selected.get("id", ""))
    bg_skills = get_background_skills(background_id)
    return background_id, bg_skills
