from pathlib import Path

import pytest

from core.asi import cap_stats
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
from core.io import load_yaml
from core.stats import apply_bonuses_to_stats

_CREATION_STATS = {
    "strength": 14,
    "dexterity": 14,
    "constitution": 12,
    "intelligence": 10,
    "wisdom": 10,
    "charisma": 10,
}


def _all_class_subclass_levels() -> list[tuple[str, str, int]]:
    data = load_yaml(Path("database/classes/classes.yaml"))
    cases: list[tuple[str, str, int]] = []
    for class_id, info in data.get("classes", {}).items():
        for sub in info.get("subclasses", []):
            subclass_id = str(sub.get("id", ""))
            if not subclass_id:
                continue
            for level in (1, 3):
                cases.append((class_id, subclass_id, level))
    return cases


def _assert_no_redundant_proficiency_feats_in_eligible(
    ctx: FeatRequirementContext,
) -> None:
    eligible, _, _ = list_feats_for_selection(ctx, [])
    for feat in eligible:
        feat_id = str(feat.get("id", ""))
        assert feat_visible_for_selection(
            feat_id, ctx
        ), f"{feat_id} eligible but adds no new proficiency"


def test_race_feat_step_required_for_variant_human():
    assert race_feat_step_required("human", "variant_human")
    assert not race_feat_step_required("human", None)
    assert not race_feat_step_required("elf", "wood_elf")


def test_feat_meets_requirements_ability_score():
    ctx = FeatRequirementContext(
        stats={"dexterity": 14, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    assert feat_meets_requirements("defensive_duelist", ctx)
    ctx_low = FeatRequirementContext(
        stats={"dexterity": 12, "strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    assert not feat_meets_requirements("defensive_duelist", ctx_low)


def test_ritual_caster_requires_intelligence_or_wisdom():
    """Интеллект 13+ или Мудрость 13+ (не оба сразу)."""
    base = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "charisma": 10,
    }
    ctx_int = FeatRequirementContext(
        stats={**base, "intelligence": 14, "wisdom": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    ctx_wis = FeatRequirementContext(
        stats={**base, "intelligence": 10, "wisdom": 14},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    ctx_neither = FeatRequirementContext(
        stats={**base, "intelligence": 12, "wisdom": 12},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
    )
    assert feat_meets_requirements("ritual_caster", ctx_int)
    assert feat_meets_requirements("ritual_caster", ctx_wis)
    assert not feat_meets_requirements("ritual_caster", ctx_neither)


def test_feat_spellcasting_requirement_needs_class_context():
    """Черты с spellcasting недоступны без класса-заклинателя."""
    ctx_no_class = FeatRequirementContext(
        stats={"strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
        has_spellcasting=False,
    )
    assert not feat_meets_requirements("war_caster", ctx_no_class)

    ctx_cleric = FeatRequirementContext(
        stats={"wisdom": 14},
        weapon_tokens=[],
        armor_tokens=["light", "medium", "shield"],
        tool_tokens=[],
        class_id="cleric",
        subclass_id="life_domain",
        level=1,
        has_spellcasting=True,
    )
    assert feat_meets_requirements("war_caster", ctx_cleric)


def test_build_feat_selection_context_from_character_uses_race_fields():
    from core.feat_visibility import (
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
    assert ctx.level == 2


def test_build_feat_selection_context_includes_class_armor():
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats={"strength": 16},
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id="fighter",
        subclass_id="champion",
        level=1,
    )
    assert "heavy" in ctx.armor_tokens
    assert ctx.has_spellcasting is False


def test_character_has_spellcasting_from_yaml():
    """Заклинания — по полям spellcasting в classes.yaml (PHB)."""
    assert character_has_spellcasting("cleric", "life_domain", 1)
    assert character_has_spellcasting("bard", "lore_college", 1)
    assert not character_has_spellcasting("fighter", "champion", 5)
    assert not character_has_spellcasting("fighter", "eldritch_knight", 2)
    assert character_has_spellcasting("fighter", "eldritch_knight", 3)
    assert not character_has_spellcasting("rogue", "thief", 5)
    assert character_has_spellcasting("rogue", "arcane_trickster", 3)


def test_resolve_feat_ability_bonuses_resilient():
    bonuses = resolve_feat_ability_bonuses(
        "resilient", {"ability": "constitution"}
    )
    assert bonuses == {"constitution": 1}


def test_skilled_feat_count_is_three():
    feat = load_feat("skilled")
    grants = feat.get("grants", [])
    assert grants[0].get("count") == 3


def test_get_feat_skill_ids_from_skilled_choices():
    picks = [
        {"type": "skill", "id": "athletics"},
        {"type": "skill", "id": "stealth"},
        {"type": "tool", "id": "thieves_tools"},
    ]
    choices = {"skilled": {"skills_tools": picks}}
    skills = get_feat_skill_ids(["skilled"], choices)
    assert skills == ["athletics", "stealth"]


def test_apply_feats_to_stats_caps_at_twenty():
    stats = {"strength": 19, "dexterity": 10}
    result = apply_feats_to_stats(
        stats,
        ["resilient"],
        {"resilient": {"ability": "strength"}},
    )
    assert result["strength"] == 20


def test_incremental_feat_bonuses_match_apply_feats_to_stats():
    """Пошаговое применение с cap совпадает с apply_feats_to_stats."""
    stats = {"strength": 19, "dexterity": 10}
    feat_ids = ["resilient", "observant"]
    feat_choices = {
        "resilient": {"ability": "strength"},
        "observant": {"ability": "dexterity"},
    }
    working = stats.copy()
    for feat_id in feat_ids:
        bonuses = resolve_feat_ability_bonuses(
            feat_id, feat_choices.get(feat_id, {})
        )
        working = cap_stats(apply_bonuses_to_stats(working, bonuses))
    assert working == apply_feats_to_stats(stats, feat_ids, feat_choices)


def test_tough_hp_adjustment_on_acquire():
    assert tough_hp_adjustment_on_acquire(4) == 8


def test_list_feats_for_selection_splits_by_requirements():
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
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert "defensive_duelist" in blocked_ids
    assert "war_caster" in blocked_ids
    assert "tough" in eligible_ids
    assert "defensive_duelist" not in eligible_ids
    assert not eligible_ids & hidden_ids
    assert not blocked_ids & hidden_ids


def test_list_feats_for_selection_puts_redundant_armor_feats_in_hidden():
    ctx = FeatRequirementContext(
        stats={"strength": 16, "dexterity": 14},
        weapon_tokens=["simple", "martial"],
        armor_tokens=["light", "medium", "heavy", "shield"],
        tool_tokens=[],
        class_id="fighter",
        skills=["athletics", "intimidation"],
    )
    eligible, blocked, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    redundant = {"heavily_armored", "lightly_armored", "moderately_armored"}
    assert redundant <= hidden_ids
    assert redundant.isdisjoint(eligible_ids)
    assert redundant.isdisjoint({str(f.get("id")) for f in blocked})
    assert "heavy_armor_master" in eligible_ids
    assert "tough" in eligible_ids


def test_list_feats_for_selection_shows_armor_feat_without_proficiency():
    ctx = FeatRequirementContext(
        stats={"strength": 10, "dexterity": 14},
        weapon_tokens=[],
        armor_tokens=["light"],
        tool_tokens=[],
        skills=[],
    )
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    assert "heavily_armored" not in eligible_ids
    assert "moderately_armored" in eligible_ids


def test_list_feats_for_selection_hides_weapon_master_when_martial_known():
    ctx = FeatRequirementContext(
        stats={"strength": 16, "dexterity": 12},
        weapon_tokens=["simple", "martial"],
        armor_tokens=[],
        tool_tokens=[],
        skills=[],
    )
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert "weapon_master" not in eligible_ids
    assert "weapon_master" in hidden_ids


@pytest.mark.parametrize(
    "class_id,subclass_id,level", _all_class_subclass_levels()
)
def test_list_feats_for_selection_no_redundant_proficiency_grants(
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
    _assert_no_redundant_proficiency_feats_in_eligible(ctx)


def test_list_feats_hides_armor_feats_for_mountain_dwarf_fighter():
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
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    redundant = {
        "heavily_armored",
        "lightly_armored",
        "moderately_armored",
        "weapon_master",
    }
    assert eligible_ids.isdisjoint(redundant)
    assert redundant <= hidden_ids


def test_list_feats_bard_valor_hides_medium_and_weapon_master_at_level_three():
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id="bard",
        subclass_id="valor_college",
        level=3,
    )
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert "moderately_armored" not in eligible_ids
    assert "weapon_master" not in eligible_ids
    assert "lightly_armored" not in eligible_ids
    hidden_armor_weapon = {
        "moderately_armored",
        "weapon_master",
        "lightly_armored",
    }
    assert hidden_armor_weapon <= hidden_ids
    assert "heavily_armored" in eligible_ids


def test_list_feats_cleric_life_hides_heavy_armor_feat():
    from core.feat_visibility import build_feat_selection_context

    ctx = build_feat_selection_context(
        stats=_CREATION_STATS,
        race_id="human",
        subrace_id="variant_human",
        background_id="soldier",
        class_id="cleric",
        subclass_id="life_domain",
        level=1,
    )
    eligible, _, hidden = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    hidden_ids = {str(f.get("id")) for f in hidden}
    assert "heavily_armored" not in eligible_ids
    assert "heavily_armored" in hidden_ids
    assert "heavy_armor_master" in eligible_ids


def test_print_feat_selection_menu_shows_hidden_section(capsys, ru_strings):
    """Скрытые черты — в конце списка, серым, без номера."""
    from ui.menus.feats import _print_feat_selection_menu

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


def test_format_feat_requirement_ability_text():
    from ui.menus.feats import _format_requirement_text

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


def test_format_or_ability_requirements_ritual_caster():
    from core.localization import load_strings
    from ui.menus.feats import (
        _format_or_ability_requirements,
        _split_feat_requirements,
    )

    feat = load_feat("ritual_caster")
    _, or_reqs = _split_feat_requirements(feat)
    strings = load_strings("ru")
    text = _format_or_ability_requirements(strings, or_reqs)
    assert text == "Интеллект или Мудрость 13 или выше"


def test_feat_summary_from_description_full_intro():
    feat = load_feat("spell_sniper")
    intro = feat_summary_description(feat)
    assert intro == (
        "Вы узнали технику, улучшающую атаку некоторыми видами заклинаний"
    )
    assert "получаете следующие преимущества" not in intro


def test_feat_full_description_benefits_only():
    feat = load_feat("spell_sniper")
    lines = feat_full_description_lines(feat)
    text = "\n".join(lines)
    assert "получаете следующие преимущества" not in text
    assert "дистанция заклинания удваивается" in text


def test_healer_full_description_from_yaml():
    feat = load_feat("healer")
    assert "stabilise" not in feat_summary_description(feat).lower()
    assert "медик" in feat_summary_description(feat).lower()
    lines = feat_full_description_lines(feat)
    text = "\n".join(lines)
    assert "комплект целителя" in text
    assert "1к6 + 4" in text
    assert "Костей Хитов" in text


def test_feat_full_description_fallback_from_features():
    feat = {
        "description": "Кратко.",
        "grants": [{"name": "Умение", "description": "Подробность умения."}],
    }
    lines = feat_full_description_lines(feat)
    assert "Подробность умения" in lines[0]


def test_creation_known_for_feat_picks_includes_race_and_background():
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
    monkeypatch, ru_strings, patch_int_input
):
    from ui.menus.feats import _pick_skills_or_tools

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


def test_pick_skills_or_tools_excludes_category_tool_pool(
    monkeypatch, ru_strings, patch_int_input
):
    from ui.menus.feats import _pick_skills_or_tools

    patch_int_input(monkeypatch, [1])
    result = _pick_skills_or_tools(
        ru_strings,
        1,
        "ru",
        known_tools=["artisans_tools"],
    )
    assert result is not None
    assert result[0]["id"] != "smith_tools"


def test_build_feat_selection_context_merges_prior_feat_skills():
    """Навыки от уже выбранных черт дополняют контекст видимости."""
    from core.equipment import all_tool_ids
    from core.feat_visibility import build_feat_selection_context
    from core.skills import PHB_SKILL_IDS

    ctx = build_feat_selection_context(
        _CREATION_STATS,
        "human",
        "variant_human",
        "soldier",
        "fighter",
        "champion",
        1,
        skills=["arcana"],
    )
    assert "arcana" in ctx.skills
    assert "athletics" in ctx.skills

    exhausted = build_feat_selection_context(
        _CREATION_STATS,
        "human",
        "variant_human",
        "soldier",
        "fighter",
        "champion",
        1,
        skills=list(PHB_SKILL_IDS),
        tool_tokens=list(all_tool_ids()),
    )
    assert not feat_visible_for_selection("skilled", exhausted)


def test_grant_skill_proficiency_choice_hidden_when_all_skills_known():
    from core.feat_visibility import _grant_adds_new_proficiency
    from core.skills import PHB_SKILL_IDS

    ctx = FeatRequirementContext(
        stats={},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
        skills=list(PHB_SKILL_IDS),
    )
    grant = {"type": "skill_proficiency", "choice": True}
    assert not _grant_adds_new_proficiency(grant, ctx)

    ctx_empty = FeatRequirementContext(
        stats={},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
        skills=[],
    )
    assert _grant_adds_new_proficiency(grant, ctx_empty)


def test_bonus_proficiencies_visibility_variants():
    from core.feat_visibility import _grant_adds_new_proficiency

    base_ctx = FeatRequirementContext(
        stats={},
        weapon_tokens=["simple"],
        armor_tokens=["light"],
        tool_tokens=[],
        skills=[],
    )
    grant_choice = {"type": "bonus_proficiencies", "choice": True}
    assert _grant_adds_new_proficiency(grant_choice, base_ctx)

    full_weapons = FeatRequirementContext(
        stats={},
        weapon_tokens=["simple", "martial"],
        armor_tokens=[],
        tool_tokens=[],
        skills=[],
    )
    grant_fixed_weapon = {
        "type": "bonus_proficiencies",
        "weapons": ["longsword"],
    }
    assert not _grant_adds_new_proficiency(grant_fixed_weapon, full_weapons)

    grant_armor = {"type": "bonus_proficiencies", "armors": ["medium"]}
    assert _grant_adds_new_proficiency(grant_armor, base_ctx)

    full_armor = FeatRequirementContext(
        stats={},
        weapon_tokens=[],
        armor_tokens=["light", "medium"],
        tool_tokens=[],
        skills=[],
    )
    assert not _grant_adds_new_proficiency(grant_armor, full_armor)

    grant_both = {
        "type": "bonus_proficiencies",
        "weapons": ["longsword"],
        "armors": ["heavy"],
    }
    assert _grant_adds_new_proficiency(grant_both, base_ctx)


def test_pick_weapons_for_feat_excludes_martial_proficiency(
    monkeypatch, ru_strings, patch_int_input
):
    from ui.menus.feats import _pick_weapons_for_feat

    patch_int_input(monkeypatch, [1])
    result = _pick_weapons_for_feat(
        ru_strings,
        1,
        "ru",
        weapon_proficiencies=["martial"],
    )
    assert result is not None
    assert "longsword" not in result


def test_apply_feat_grants_to_character_merges_skills_and_tools():
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
    choices = {
        "skills_tools": [
            {"type": "skill", "id": "athletics"},
            {"type": "skill", "id": "stealth"},
            {"type": "tool", "id": "thieves_tools"},
        ]
    }
    updated = apply_feat_grants_to_character(char, "skilled", choices)

    assert updated.skills == ["perception", "athletics", "stealth"]
    assert "thieves_tools" in updated.tool_proficiencies
    assert "gaming_set_dice" in updated.tool_proficiencies
