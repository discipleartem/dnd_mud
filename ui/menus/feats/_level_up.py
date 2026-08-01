"""Выбор ASI или черт при левелапе."""

from typing import Any

from core.character.models import Character
from core.feats.apply import apply_feat_pick
from core.feats.requirements import (
    build_feat_selection_context_from_character,
    list_feats_for_selection,
)
from core.platform.localization import get_string
from core.progression.asi import apply_asi_pick
from core.types import StatMap, StringsDict
from ui.menus.console import print_screen_header
from ui.menus.feats._selection import _pick_feat_from_lists
from ui.menus.feats._subchoices import _resolve_feat_subchoices


def select_level_up_feat_or_asi(
    strings: StringsDict,
    character: Character,
    new_level: int,
    language: str = "ru",
) -> (
    tuple[Character, StatMap, list[str], dict[str, dict[str, Any]], str] | None
):
    """Выбор ASI или черты при левелапе.

    Возвращает (character, stats, feat_ids, feat_choices, asi_choice_value)
    или None при отмене.
    """
    from ui.menus.progression.asi import select_asi_mode, select_asi_stats

    print_screen_header(
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
        stats = apply_asi_pick(stats, picks)
        return character, stats, feat_ids, feat_choices, "asi"

    ctx = build_feat_selection_context_from_character(character)
    eligible, blocked, hidden = list_feats_for_selection(ctx, feat_ids)
    if not eligible:
        print(get_string(strings, "character.feat_none_available"))
        print()
        return None

    print_screen_header(get_string(strings, "character.feat_caption"))
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
    stats = apply_feat_pick(stats, feat_id, sub)
    asi_value = f"feat:{feat_id}"
    return character, stats, feat_ids, feat_choices, asi_value
