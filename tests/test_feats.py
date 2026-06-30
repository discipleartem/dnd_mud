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
    feat_visible_for_selection,
    get_feat_skill_ids,
    list_feats_for_selection,
    load_feat,
    race_feat_step_required,
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


def test_race_feat_step_and_requirements() -> None:
    assert race_feat_step_required("human", "variant_human")
    assert not race_feat_step_required("elf", "wood_elf")

    ctx_ok = FeatRequirementContext(
        stats={"dexterity": 14, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    ctx_low = FeatRequirementContext(
        stats={"dexterity": 12, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    assert feat_meets_requirements("defensive_duelist", ctx_ok)
    assert not feat_meets_requirements("defensive_duelist", ctx_low)

    base = dict.fromkeys(
        [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ],
        10,
    )
    assert feat_meets_requirements(
        "ritual_caster",
        FeatRequirementContext(
            stats={**base, "intelligence": 14},
            weapon_tokens=[],
            armor_tokens=[],
            tool_tokens=[],
        ),
    )
    assert not feat_meets_requirements(
        "war_caster",
        FeatRequirementContext(
            stats={"strength": 10},
            weapon_tokens=[],
            armor_tokens=[],
            tool_tokens=[],
            has_spellcasting=False,
        ),
    )


def test_feat_selection_context_and_spellcasting() -> None:
    from core.feat_visibility import (
        build_feat_selection_context,
        build_feat_selection_context_from_character,
    )
    from core.models import Character

    character = Character(
        name="Elf",
        race="elf",
        subrace="high_elf",
        class_id="wizard",
        level=1,
        stats=dict.fromkeys(
            [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ],
            10,
        ),
    )
    ctx = build_feat_selection_context_from_character(character)
    assert ctx.race_id == "elf"
    assert ctx.subrace_id == "high_elf"

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


@pytest.mark.parametrize(
    "ctx_kwargs,check",
    [
        (
            {
                "stats": {"dexterity": 12, "strength": 10},
                "weapon_tokens": [],
                "armor_tokens": [],
                "tool_tokens": [],
                "has_spellcasting": False,
            },
            "requirements_split",
        ),
        (
            {
                "stats": {"strength": 16, "dexterity": 14},
                "weapon_tokens": ["simple", "martial"],
                "armor_tokens": ["light", "medium", "heavy", "shield"],
                "tool_tokens": [],
                "class_id": "fighter",
                "skills": ["athletics", "intimidation"],
            },
            "redundant_armor_hidden",
        ),
    ],
)
def test_list_feats_for_selection_visibility(
    ctx_kwargs: dict[str, Any], check: str
) -> None:
    ctx = FeatRequirementContext(**ctx_kwargs)
    eligible, blocked, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    blocked_ids = {str(f.get("id")) for f in blocked}
    hidden_ids = {str(f.get("id")) for f in hidden}

    if check == "requirements_split":
        assert "defensive_duelist" in blocked_ids
        assert "tough" in eligible_ids
        assert not eligible_ids & hidden_ids
    else:
        redundant = {
            "heavily_armored",
            "lightly_armored",
            "moderately_armored",
        }
        assert redundant <= hidden_ids
        assert redundant.isdisjoint(eligible_ids)


@pytest.mark.parametrize(
    "class_id,subclass_id,level",
    [
        ("fighter", "champion", 1),
        ("cleric", "life_domain", 1),
        ("bard", "valor_college", 3),
    ],
)
def test_list_feats_no_redundant_proficiency_grants(
    class_id: str, subclass_id: str, level: int
) -> None:
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id=class_id,
        subclass_id=subclass_id,
        level=level,
    )
    eligible, _, _ = list_feats_for_selection(ctx, [])
    for feat in eligible:
        feat_id = str(feat.get("id", ""))
        assert feat_visible_for_selection(feat_id, ctx)


@pytest.mark.parametrize(
    "race_id,subrace_id,class_id,subclass_id,level,hidden_subset",
    [
        (
            "dwarf",
            "mountain_dwarf",
            "fighter",
            "champion",
            1,
            {"heavily_armored", "weapon_master"},
        ),
        (
            "human",
            "variant_human",
            "cleric",
            "life_domain",
            1,
            {"heavily_armored"},
        ),
    ],
)
def test_list_feats_hides_redundant_proficiency_feats(
    race_id: str,
    subrace_id: str,
    class_id: str,
    subclass_id: str,
    level: int,
    hidden_subset: set[str],
) -> None:
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id=race_id,
        subrace_id=subrace_id,
        background_id="soldier",
        class_id=class_id,
        subclass_id=subclass_id,
        level=level,
    )
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert hidden_subset <= hidden_ids
    assert eligible_ids.isdisjoint(hidden_subset)


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
    """Скрытые черты — в конце списка, серым, без номера."""
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
    eligible_part = out[:hidden_idx]
    hidden_part = out[hidden_idx:]
    assert "Знаток тяжёлых доспехов" in hidden_part
    assert "Знаток тяжёлых доспехов" not in eligible_part
    assert "Крепкий" in eligible_part


def test_format_feat_requirement_ability_text() -> None:
    from ui.menus.feats._requirements import _format_requirement_text

    strings = {
        "character": {
            "feat_req_ability": "{ability} {value}+ (сейчас {current})",
        },
        "stats": {"dexterity": "Ловкость"},
    }
    ctx = FeatRequirementContext(
        stats={"dexterity": 12},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    text = _format_requirement_text(
        strings,
        {"type": "ability_score", "target": "dexterity", "value": 13},
        ctx,
        "ru",
    )
    assert text == "Ловкость 13+ (сейчас 12)"


def test_format_or_ability_requirements_ritual_caster() -> None:
    from core.localization import load_strings
    from ui.menus.feats._requirements import (
        _format_or_ability_requirements,
        _split_feat_requirements,
    )

    feat = load_feat("ritual_caster")
    _, or_reqs = _split_feat_requirements(feat)
    strings = load_strings("ru")
    text = _format_or_ability_requirements(strings, or_reqs)
    assert text == "Интеллект или Мудрость 13 или выше"


def test_feat_full_description_benefits_only() -> None:
    feat = load_feat("spell_sniper")
    lines = feat_full_description_lines(feat)
    text = "\n".join(lines)
    assert "получаете следующие преимущества" not in text
    assert "дистанция заклинания удваивается" in text


def test_healer_full_description_from_yaml() -> None:
    feat = load_feat("healer")
    assert "stabilise" not in feat_summary_description(feat).lower()
    assert "медик" in feat_summary_description(feat).lower()
    lines = feat_full_description_lines(feat)
    text = "\n".join(lines)
    assert "комплект целителя" in text
    assert "1к6 + 4" in text
    assert "Костей Хитов" in text


def test_feat_full_description_fallback_from_features() -> None:
    feat = {
        "description": "Кратко.",
        "grants": [{"name": "Умение", "description": "Подробность умения."}],
    }
    lines = feat_full_description_lines(feat)
    assert "Подробность умения" in lines[0]


def test_creation_known_for_feat_picks_includes_race_and_background() -> None:
    from core.feat_visibility import creation_known_for_feat_picks

    skills, tools, weapons = creation_known_for_feat_picks(
        "human",
        "variant_human",
        "soldier",
        "fighter",
        "champion",
        1,
    )
    assert "athletics" in skills
    assert "intimidation" in skills
    assert "martial" in weapons


def test_pick_skills_or_tools_excludes_known(
    monkeypatch: pytest.MonkeyPatch,
    ru_strings: dict[str, Any],
    patch_int_input: Any,
) -> None:
    from ui.menus.feats._subchoices import _pick_skills_or_tools

    patch_int_input(monkeypatch, [1])
    result = _pick_skills_or_tools(
        ru_strings,
        1,
        "ru",
        known_skills=["athletics", "perception"],
        known_tools=["thieves_tools"],
    )
    assert result is not None
    picked_id = result[0]["id"]
    assert picked_id not in ("athletics", "perception", "thieves_tools")
