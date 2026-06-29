"""Тесты резолвера черт."""

from core.asi import cap_stats
from core.classes import character_has_spellcasting
from core.feats import (
    FeatRequirementContext,
    apply_feats_to_stats,
    feat_full_description_lines,
    feat_meets_requirements,
    feat_summary_description,
    get_feat_skill_ids,
    list_feats_for_selection,
    load_feat,
    race_feat_step_required,
    resolve_feat_ability_bonuses,
    tough_hp_adjustment_on_acquire,
)
from core.stats import apply_bonuses_to_stats


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


def test_feat_ctx_at_creation_includes_class_armor():
    from ui.menus.feats import _feat_ctx_at_creation

    ctx = _feat_ctx_at_creation(
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
    features = feat.get("features", [])
    mechanics = features[0]["mechanics"]
    assert mechanics.get("count") == 3


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
    eligible, blocked = list_feats_for_selection(ctx, [])
    eligible_ids = {str(f.get("id")) for f in eligible}
    blocked_ids = {str(f.get("id")) for f in blocked}
    assert "defensive_duelist" in blocked_ids
    assert "war_caster" in blocked_ids
    assert "tough" in eligible_ids
    assert "defensive_duelist" not in eligible_ids


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
        "features": [{"name": "Умение", "description": "Подробность умения."}],
    }
    lines = feat_full_description_lines(feat)
    assert "Подробность умения" in lines[0]
