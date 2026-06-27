"""Повышение уровня персонажа (PHB): HP по режиму сложности."""

from colorama import Fore, Style

from core.dice import ability_modifier
from core.localization import get_string
from core.models import Character
from core.progression import (
    apply_level_up,
    has_pending_level_up,
    roll_hp_gain_for_level_up,
)
from core.types import LanguageCode, StringsDict
from ui.menus._common import _press_enter, _print_screen_header


def run_pending_level_ups(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character:
    """Пошагово применить все ожидающие повышения уровня."""
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        gain, dice_roll = roll_hp_gain_for_level_up(
            char.class_name,
            char.stats,
            new_level,
            char.difficulty,
        )
        _print_level_up_screen(strings, char, new_level, gain, dice_roll)
        _press_enter(strings)
        char = apply_level_up(char, gain)
    return char


def _print_level_up_screen(
    strings: StringsDict,
    character: Character,
    new_level: int,
    hp_gain: int,
    dice_roll: int | None,
) -> None:
    """Экран одного повышения уровня."""
    _print_screen_header(get_string(strings, "level_up.caption"))
    reached = get_string(strings, "level_up.reached", level=new_level)
    print(f"{Fore.YELLOW}{Style.BRIGHT}{reached}{Style.RESET_ALL}")
    print()

    con_mod = ability_modifier(character.stats.get("constitution", 10))
    if dice_roll is not None:
        hp_line = get_string(
            strings,
            "level_up.hp_gain_roll",
            roll=dice_roll,
            con_mod=con_mod,
            gain=hp_gain,
        )
    else:
        hp_line = get_string(strings, "level_up.hp_gain_average", gain=hp_gain)
    print(f"{Fore.CYAN}{hp_line}{Style.RESET_ALL}")
    print()

    preview_max = character.max_hp + hp_gain
    preview_current = character.current_hp + hp_gain
    totals = get_string(
        strings,
        "level_up.hp_totals",
        current=preview_current,
        max_hp=preview_max,
    )
    print(totals)
    print()
