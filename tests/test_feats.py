from typing import Any

import pytest

from core.classes import character_has_spellcasting
from core.feats import (
    FeatRequirementContext,
    apply_feat_grants_to_character,
    apply_feats_to_stats,
    feat_full_description_lines,
    feat_meets_requirements,
    feat_summary_description,
    get_feat_skill_ids,
    list_feats_for_selection,
    load_feat,
    resolve_feat_ability_bonuses,
    tough_hp_adjustment_on_acquire,
)

_CREATION_STATS = {
    "strength": 14,
    "dexterity": 14,
    "constitution": 12,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_feat_meets_requirements_and_spellcasting_context() -> None:
    from core.feat_visibility import build_feat_selection_context

    ctx_ok = FeatRequirementContext(
        stats={"dexterity": 14, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    assert feat_meets_requirements("defensive_duelist", ctx_ok)
    assert not feat_meets_requirements(
        "defensive_duelist",
        FeatRequirementContext(
            stats={"dexterity": 12, "strength": 10},
            weapon_tokens=[],
            armor_tokens=[],
            tool_tokens=[],
        ),
    )
    fighter_ctx = build_feat_selection_context(
        stats={"strength": 16},
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id="fighter",
        subclass_id="champion",
        level=1,
    )
    assert "heavy" in fighter_ctx.armor_tokens
    assert character_has_spellcasting("fighter", "eldritch_knight", 3)


def test_apply_feats_and_skilled_grants() -> None:
    assert resolve_feat_ability_bonuses(
        "resilient", {"ability": "constitution"}
    ) == {"constitution": 1}
    assert tough_hp_adjustment_on_acquire(4) == 8
    stats = {"strength": 19, "dexterity": 10}
    assert (
        apply_feats_to_stats(
            stats,
            ["resilient"],
            {"resilient": {"ability": "strength"}},
        )["strength"]
        == 20
    )
    skills = get_feat_skill_ids(
        ["skilled"],
        {
            "skilled": {
                "skills_tools": [
                    {"type": "skill", "id": "athletics"},
                    {"type": "tool", "id": "thieves_tools"},
                ]
            }
        },
    )
    assert skills == ["athletics"]


def test_list_feats_for_selection_requirements_split() -> None:
    ctx = FeatRequirementContext(
        stats={"dexterity": 12, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
        has_spellcasting=False,
    )
    eligible, blocked, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    blocked_ids = {str(f.get("id")) for f in blocked}
    assert "defensive_duelist" in blocked_ids
    assert "tough" in eligible_ids
    assert not eligible_ids & {str(f.get("id")) for f in hidden}


def test_redundant_proficiency_feats_hidden_fighter() -> None:
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id="fighter",
        subclass_id="champion",
        level=1,
    )
    hidden_subset = {
        "heavily_armored",
        "lightly_armored",
        "moderately_armored",
    }
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert hidden_subset <= hidden_ids
    assert eligible_ids.isdisjoint(hidden_subset)


def test_redundant_proficiency_feats_hidden_dwarf() -> None:
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id="dwarf",
        subrace_id="mountain_dwarf",
        background_id="soldier",
        class_id="fighter",
        subclass_id="champion",
        level=1,
    )
    hidden_subset = {"heavily_armored", "weapon_master"}
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert hidden_subset <= hidden_ids


def test_apply_feat_grants_to_character_merges_skills_and_tools() -> None:
    from core.models import Character

    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=4,
        stats={"constitution": 14},
        current_hp=30,
        max_hp=30,
        skills=["perception"],
        tool_proficiencies=["gaming_set_dice"],
    )
    updated = apply_feat_grants_to_character(
        char,
        "skilled",
        {
            "skills_tools": [
                {"type": "skill", "id": "athletics"},
                {"type": "tool", "id": "thieves_tools"},
            ]
        },
    )
    assert "athletics" in updated.skills
    assert "thieves_tools" in updated.tool_proficiencies


def test_print_feat_selection_menu_shows_hidden_section(
    capsys: pytest.CaptureFixture[str],
    ru_strings: dict[str, Any],
) -> None:
    from ui.menus.feats._selection import _print_feat_selection_menu

    ctx = FeatRequirementContext(
        stats={"strength": 16, "dexterity": 14},
        weapon_tokens=["simple", "martial"],
        armor_tokens=["light", "medium", "heavy", "shield"],
        tool_tokens=[],
        class_id="fighter",
        skills=["athletics", "intimidation"],
    )
    eligible, blocked, hidden = list_feats_for_selection(ctx, [])
    _print_feat_selection_menu(
        ru_strings, eligible, blocked, hidden, ctx, "ru"
    )
    out = capsys.readouterr().out
    hidden_idx = out.find("Скрыто")
    assert hidden_idx >= 0
    assert "Знаток тяжёлых доспехов" in out[hidden_idx:]


@pytest.mark.parametrize(
    "feat,expected_substrings",
    [
        ("spell_sniper", ["дистанция заклинания удваивается"]),
        ("healer", ["комплект целителя", "1к6 + 4"]),
    ],
)
def test_feat_full_description_lines(
    feat: str, expected_substrings: list[str]
) -> None:
    feat_data = load_feat(feat)
    if feat == "healer":
        summary = feat_summary_description(feat_data)
        assert "медик" in summary.lower()
    lines = feat_full_description_lines(feat_data)
    text = "\n".join(lines)
    for substring in expected_substrings:
        assert substring in text
