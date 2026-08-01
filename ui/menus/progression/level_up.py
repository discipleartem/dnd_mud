"""Повышение уровня персонажа (PHB): ASI/черта и HP по режиму сложности."""

from colorama import Fore, Style

from core.character.models import Character
from core.feats.catalog import load_feat
from core.platform.localization import get_string
from core.progression.asi import feat_id_from_asi_choice, pending_asi_at_level
from core.progression.hp import HpGainBreakdown
from core.progression.level_up import (
    AsiResolution,
    process_pending_level_ups,
    resolve_level_up_asi,
)
from core.types import LanguageCode, StringsDict
from ui.menus.console import press_enter, print_screen_header
from ui.menus.feats import select_level_up_feat_or_asi


def _print_level_up_screen(
    strings: StringsDict,
    character: Character,
    new_level: int,
    breakdown: HpGainBreakdown,
    extra_hp: int = 0,
) -> None:
    """Экран одного повышения уровня."""
    print_screen_header(get_string(strings, "level_up.caption"))
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
        result = select_level_up_feat_or_asi(
            strings, char, new_level, language
        )
        if result is None:
            return None
        _character, stats, feat_ids, feat_choices, asi_value = result
        resolution = resolve_level_up_asi(
            char,
            new_level,
            stats=stats,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
            asi_value=asi_value,
        )
        feat_id = feat_id_from_asi_choice(asi_value)
        if feat_id:
            feat = load_feat(feat_id)
            feat_name = feat.get("name", feat_id)
            msg = get_string(strings, "level_up.feat_taken", name=feat_name)
            print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
            print()
        return resolution

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
        press_enter(strings)
        return True

    return process_pending_level_ups(
        character,
        resolve_asi=resolve_asi_ui,
        on_level_up=on_level_up_ui,
    )
