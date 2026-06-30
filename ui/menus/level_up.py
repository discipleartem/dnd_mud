"""Повышение уровня персонажа (PHB): ASI/черта и HP по режиму сложности."""

from dataclasses import replace

from colorama import Fore, Style

from core.asi import (
    con_hp_bonus_from_asi,
    feat_id_from_asi_choice,
    pending_asi_at_level,
)
from core.feats import (
    apply_feat_grants_to_character,
    load_feat,
    tough_hp_adjustment_on_acquire,
)
from core.localization import get_string
from core.models import Character
from core.progression import (
    AsiResolution,
    HpGainBreakdown,
    process_pending_level_ups,
)
from core.types import LanguageCode, StringsDict
from ui.menus._common import _press_enter, _print_screen_header
from ui.menus.feats import select_level_up_feat_or_asi


def _print_level_up_screen(
    strings: StringsDict,
    character: Character,
    new_level: int,
    breakdown: HpGainBreakdown,
    extra_hp: int = 0,
) -> None:
    """Экран одного повышения уровня."""
    _print_screen_header(get_string(strings, "level_up.caption"))
    reached = get_string(strings, "level_up.reached", level=new_level)
    print(f"{Fore.YELLOW}{Style.BRIGHT}{reached}{Style.RESET_ALL}")
    print()

    for line in _format_hp_gain_lines(strings, breakdown):
        print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
    print()

    total_gain = breakdown.total + extra_hp
    preview_max = character.max_hp + total_gain
    preview_current = character.current_hp + total_gain
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


def run_pending_level_ups(
    strings: StringsDict,
    character: Character,
    language: LanguageCode = "ru",
) -> Character:
    """Пошагово применить все ожидающие повышения уровня."""

    def resolve_asi_ui(
        char: Character, new_level: int
    ) -> AsiResolution | None:
        if not pending_asi_at_level(char, new_level):
            return None
        old_stats = char.stats.copy()
        had_tough = "tough" in char.feat_ids
        result = select_level_up_feat_or_asi(
            strings, char, new_level, language
        )
        if result is None:
            return None
        updated, stats, feat_ids, feat_choices, asi_value = result
        asi_choices = dict(updated.asi_choices)
        asi_choices[str(new_level)] = asi_value
        con_bonus = con_hp_bonus_from_asi(old_stats, stats, new_level)
        char = replace(
            updated,
            stats=stats,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
            asi_choices=asi_choices,
        )
        feat_id = feat_id_from_asi_choice(asi_value)
        if feat_id:
            char = apply_feat_grants_to_character(
                char, feat_id, feat_choices.get(feat_id, {})
            )
            feat = load_feat(feat_id)
            feat_name = feat.get("name", feat_id)
            msg = get_string(strings, "level_up.feat_taken", name=feat_name)
            print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
            print()
        tough_bonus = 0
        if feat_id == "tough" and not had_tough:
            tough_bonus = tough_hp_adjustment_on_acquire(new_level)
        return AsiResolution(
            character=char, con_bonus=con_bonus, tough_bonus=tough_bonus
        )

    def on_level_up_ui(
        char: Character,
        new_level: int,
        breakdown: HpGainBreakdown,
        con_bonus: int,
        tough_bonus: int,
    ) -> bool:
        extra = con_bonus + tough_bonus
        _print_level_up_screen(strings, char, new_level, breakdown, extra)
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
        return True

    return process_pending_level_ups(
        character,
        resolve_asi=resolve_asi_ui,
        on_level_up=on_level_up_ui,
    )
