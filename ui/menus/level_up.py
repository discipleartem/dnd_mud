"""Повышение уровня персонажа (PHB): ASI/черта и HP по режиму сложности."""

from dataclasses import replace

from colorama import Fore, Style

from core.asi import con_hp_bonus_from_asi, pending_asi_at_level
from core.feats import load_feat, tough_hp_adjustment_on_acquire
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
from ui.menus.feats import select_level_up_feat_or_asi


def run_pending_level_ups(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character:
    """Пошагово применить все ожидающие повышения уровня."""
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        old_stats = char.stats.copy()
        con_bonus = 0
        tough_bonus = 0

        if pending_asi_at_level(char, new_level):
            result = select_level_up_feat_or_asi(
                strings, char, new_level, language
            )
            if result is None:
                break
            char, stats, feat_ids, feat_choices, asi_value = result
            asi_choices = dict(char.asi_choices)
            asi_choices[str(new_level)] = asi_value
            con_bonus = con_hp_bonus_from_asi(old_stats, stats, char.level)
            had_tough = "tough" in character.feat_ids
            char = replace(
                char,
                stats=stats,
                feat_ids=feat_ids,
                feat_choices=feat_choices,
                asi_choices=asi_choices,
            )
            if asi_value.startswith("feat:tough") and not had_tough:
                tough_bonus = tough_hp_adjustment_on_acquire(new_level)
            if asi_value.startswith("feat:"):
                feat_id = asi_value.split(":", 1)[1]
                feat = load_feat(feat_id)
                feat_name = feat.get("name", feat_id)
                msg = get_string(
                    strings, "level_up.feat_taken", name=feat_name
                )
                print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
                print()

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
        if con_bonus:
            msg = get_string(strings, "level_up.con_hp_bonus", bonus=con_bonus)
            print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")
        if tough_bonus:
            msg = get_string(
                strings, "level_up.tough_hp_bonus", bonus=tough_bonus
            )
            print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")
        if con_bonus or tough_bonus:
            print()
        _press_enter(strings)
        extra = con_bonus + tough_bonus
        char = apply_level_up(char, breakdown.total + extra)
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
