"""Тесты резолвера черт."""

from core.feats import (
    FeatRequirementContext,
    apply_feats_to_stats,
    feat_meets_requirements,
    get_feat_skill_ids,
    load_feat,
    race_feat_step_required,
    resolve_feat_ability_bonuses,
    tough_hp_adjustment_on_acquire,
)


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


def test_feat_meets_requirements_spellcasting_hidden_at_creation():
    ctx = FeatRequirementContext(
        stats={"strength": 10},
        weapon_tokens=[],
        armor_tokens=[],
        tool_tokens=[],
        has_spellcasting=False,
    )
    assert not feat_meets_requirements("war_caster", ctx)


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


def test_tough_hp_adjustment_on_acquire():
    assert tough_hp_adjustment_on_acquire(4) == 8
