"""Выбор ASI или черты при левелапе."""

from typing import Any

from core.asi import cap_stats
from core.feat_visibility import build_feat_selection_context_from_character
from core.feats import (
    list_feats_for_selection,
    resolve_feat_ability_bonuses,
)
from core.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header
from ui.menus.feats._selection import _pick_feat_from_lists
from ui.menus.feats._subchoices import _resolve_feat_subchoices


def select_level_up_feat_or_asi(
    strings: StringsDict,
    character: Any,
    new_level: int,
    language: str = "ru",
) -> tuple[Any, StatMap, list[str], dict[str, dict[str, Any]], str] | None:
    """Выбор ASI или черты при левелапе.

    Возвращает (character, stats, feat_ids, feat_choices, asi_choice_value)
    или None при отмене.
    """
    from dataclasses import replace

    from core.asi import apply_asi_one_two, apply_asi_two_one
    from ui.menus.asi import select_asi_mode, select_asi_stats

    _print_screen_header(
        get_string(
            strings,
            "level_up.asi_feature_heading",
            level=new_level,
        )
    )
    mode = select_asi_mode(strings)
    if mode is None:
        return None

    stats = character.stats.copy()
    feat_ids = list(character.feat_ids)
    feat_choices = dict(character.feat_choices)

    if mode == "asi":
        picks = select_asi_stats(strings, stats)
        if picks is None:
            return None
        if picks[0] == picks[1]:
            stats = apply_asi_two_one(stats, picks[0])
        else:
            stats = apply_asi_one_two(stats, picks[0], picks[1])
        stats = cap_stats(stats)
        updated = replace(character, stats=stats)
        return updated, stats, feat_ids, feat_choices, "asi"

    ctx = build_feat_selection_context_from_character(character)
    eligible, blocked, hidden = list_feats_for_selection(ctx, feat_ids)
    if not eligible:
        print(get_string(strings, "character.feat_none_available"))
        print()
        return None

    _print_screen_header(get_string(strings, "character.feat_caption"))
    selected = _pick_feat_from_lists(
        strings, eligible, blocked, hidden, ctx, language
    )
    if selected is None:
        return None
    feat_id = str(selected.get("id", ""))
    sub = _resolve_feat_subchoices(
        strings,
        feat_id,
        stats,
        language,
        known_languages=character.languages,
        known_skills=list(character.skills),
        known_tools=list(character.tool_proficiencies),
        weapon_proficiencies=list(character.weapon_proficiencies),
    )
    if sub is None:
        return None

    feat_choices[feat_id] = sub
    feat_ids.append(feat_id)
    bonuses = resolve_feat_ability_bonuses(feat_id, sub)
    stats = cap_stats(_deps.apply_bonuses_to_stats(stats, bonuses))
    updated = replace(
        character,
        stats=stats,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
    )
    asi_value = f"feat:{feat_id}"
    return updated, stats, feat_ids, feat_choices, asi_value
