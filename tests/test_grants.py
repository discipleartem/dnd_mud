"""Тесты нормализации grants."""

from core.grants import (
    feature_to_grants,
    grants_from_entity,
    inherit_flags,
    normalize_grant,
)
from core.races import (
    clear_races_cache,
    collect_race_grants,
    get_race_bonuses,
    resolve_subrace_id,
)


def test_normalize_grant_maps_ability_bonus():
    grant = normalize_grant(
        {"type": "ability_bonus", "count": 2, "value": 1, "choice": True}
    )
    assert grant["type"] == "ability_increase"
    assert grant["amount"] == 1


def test_feature_to_grants_legacy_skill():
    feats = feature_to_grants(
        {
            "type": "skill_proficiency",
            "mechanics": {"skills": ["perception"]},
        }
    )
    assert feats[0]["type"] == "skill_proficiency"
    assert feats[0]["skills"] == ["perception"]


def test_human_standard_bonuses():
    clear_races_cache()
    bonuses = get_race_bonuses("human", "standard")
    assert bonuses.get("strength") == 1
    assert bonuses.get("charisma") == 1


def test_human_resolve_subrace_fallback():
    clear_races_cache()
    assert resolve_subrace_id("human", None) == "standard"


def test_variant_human_grants_no_inherit():
    clear_races_cache()
    grants = collect_race_grants("human", "variant_human")
    types = [g.get("type") for g in grants]
    assert "ability_increase" in types
    assert "feat" in types
    assert "language" not in types


def test_inherit_flags_new_and_legacy():
    assert inherit_flags(
        {"inherit": {"ability_bonuses": False, "grants": False}}
    ) == (False, False)
    assert inherit_flags(
        {"inherit_base_bonuses": False, "inherit_base_features": True}
    ) == (False, True)


def test_grants_from_entity_prefers_grants_key():
    entity = {
        "grants": [{"type": "language", "count": 1, "choice": True}],
        "features": [{"type": "darkvision", "mechanics": {"range": 60}}],
    }
    grants = grants_from_entity(entity)
    assert len(grants) == 1
    assert grants[0]["type"] == "language"
