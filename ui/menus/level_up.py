"""Повышение уровня персонажа (PHB): HP по режиму сложности."""

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.progression import (
    HpGainBreakdown,
    apply_level_up,
    has_pending_level_up,
    hp_gain_breakdown_for_level_up,
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
        breakdown = hp_gain_breakdown_for_level_up(
            char.class_name,
            char.stats,
            new_level,
            char.difficulty,
            char.race,
            char.subrace,
            char.feat_ids,
        )
        _print_level_up_screen(strings, char, new_level, breakdown)
        _press_enter(strings)
        char = apply_level_up(char, breakdown.total)
    return char


def _print_level_up_screen(
    strings: StringsDict,
    character: Character,
    new_level: int,
    breakdown: HpGainBreakdown,
) -> None:
    """Экран одного повышения уровня."""
    _print_screen_header(get_string(strings, "level_up.caption"))
    reached = get_string(strings, "level_up.reached", level=new_level)
    print(f"{Fore.YELLOW}{Style.BRIGHT}{reached}{Style.RESET_ALL}")
    print()

    for line in _format_hp_gain_lines(strings, breakdown):
        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
    print()

    preview_max = character.max_hp + breakdown.total
    preview_current = character.current_hp + breakdown.total
    totals = get_string(
        strings,
        "level_up.hp_totals",
        current=preview_current,
        max_hp=preview_max,
    )
    print(totals)
    print()


def _format_hp_gain_lines(
    strings: StringsDict, breakdown: HpGainBreakdown
) -> list[str]:
    """Строки прироста HP: кость + CON отдельно от расовых/чертовых бонусов."""
    lines: list[str] = []
    if breakdown.dice_roll is not None:
        lines.append(
            get_string(
                strings,
                "level_up.hp_gain_roll",
                roll=breakdown.dice_roll,
                con_mod=breakdown.con_mod,
                class_part=breakdown.class_part,
            )
        )
    elif breakdown.is_first_level:
        lines.append(
            get_string(
                strings,
                "level_up.hp_gain_first_level",
                die=breakdown.die_part,
                con_mod=breakdown.con_mod,
                class_part=breakdown.class_part,
            )
        )
    else:
        lines.append(
            get_string(
                strings,
                "level_up.hp_gain_average",
                die_part=breakdown.die_part,
                con_mod=breakdown.con_mod,
                class_part=breakdown.class_part,
            )
        )
    if breakdown.bonus_sources:
        for source in breakdown.bonus_sources:
            lines.append(
                get_string(
                    strings,
                    "level_up.hp_gain_bonus_named",
                    name=source.name,
                    bonus=source.amount,
                )
            )
    lines.append(
        get_string(strings, "level_up.hp_gain_total", total=breakdown.total)
    )
    return lines
