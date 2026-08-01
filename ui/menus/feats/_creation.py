"""Выбор черт при создании персонажа."""

from typing import Any

from core.feats.apply import apply_feat_pick, apply_feats_to_stats
from core.feats.catalog import get_race_feat_grants
from core.feats.requirements import (
    build_feat_selection_context,
    creation_known_for_feat_picks,
    list_feats_for_selection,
)
from core.feats.selection_side_effects import (
    accumulate_feat_proficiency_knowledge,
)
from core.platform.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus.console import print_screen_header
from ui.menus.feats._selection import _pick_feat_from_lists
from ui.menus.feats._subchoices import _resolve_feat_subchoices


def select_creation_feats(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    stats: StatMap,
    background_id: str | None,
    language: str = "ru",
    *,
    class_id: str,
    subclass_id: str | None = None,
    start_level: int = 1,
    known_languages: list[str] | None = None,
) -> tuple[list[str], dict[str, dict[str, Any]], StatMap] | None:
    """Выбор расовых черт; None — назад."""
    grants = get_race_feat_grants(race_id, subrace_id)
    if not grants:
        return [], {}, stats

    feat_ids: list[str] = []
    feat_choices: dict[str, dict[str, Any]] = {}
    working_stats = stats.copy()
    pick_total = sum(g.count for g in grants)
    pick_current = 0
    known_skills, known_tools, weapon_profs = creation_known_for_feat_picks(
        race_id,
        subrace_id,
        background_id,
        class_id,
        subclass_id,
        start_level,
    )

    for grant in grants:
        for _ in range(grant.count):
            pick_current += 1
            ctx = build_feat_selection_context(
                working_stats,
                race_id,
                subrace_id,
                background_id,
                class_id,
                subclass_id,
                start_level,
                skills=known_skills,
                weapon_tokens=weapon_profs,
                tool_tokens=known_tools,
            )
            eligible, blocked, hidden = list_feats_for_selection(ctx, feat_ids)
            if not eligible:
                print_screen_header(
                    get_string(strings, "character.feat_caption")
                )
                print(get_string(strings, "character.feat_none_available"))
                print()
                return None

            print_screen_header(get_string(strings, "character.feat_caption"))
            print(
                get_string(
                    strings,
                    "character.feat_pick_heading",
                    current=pick_current,
                    total=pick_total,
                )
            )
            print()
            selected = _pick_feat_from_lists(
                strings, eligible, blocked, hidden, ctx, language
            )
            if selected is None:
                return None
            feat_id = str(selected.get("id", ""))
            sub = _resolve_feat_subchoices(
                strings,
                feat_id,
                working_stats,
                language,
                known_languages=known_languages,
                known_skills=known_skills,
                known_tools=known_tools,
                weapon_proficiencies=weapon_profs,
            )
            if sub is None:
                return None

            feat_choices[feat_id] = sub
            feat_ids.append(feat_id)
            working_stats = apply_feat_pick(working_stats, feat_id, sub)
            accumulate_feat_proficiency_knowledge(
                feat_id,
                sub,
                weapon_profs=weapon_profs,
                known_skills=known_skills,
                known_tools=known_tools,
            )

    final_stats = apply_feats_to_stats(stats, feat_ids, feat_choices)
    return feat_ids, feat_choices, final_stats
