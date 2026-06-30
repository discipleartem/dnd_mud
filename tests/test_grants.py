"""Тесты нормализации grants."""

from core.grants import (
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


def test_grants_from_entity_skill_proficiency():
    entity = {
        "grants": [
            {"type": "skill_proficiency", "skills": ["perception"]},
        ],
    }
    grants = grants_from_entity(entity)
    assert grants[0]["type"] == "skill_proficiency"
    assert grants[0]["skills"] == ["perception"]


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
    assert "language" in types
    assert types.count("language") == 1


def test_inherit_flags_new_and_legacy():
    assert inherit_flags(
        {"inherit": {"ability_bonuses": False, "grants": False}}
    ) == (False, False)
    assert inherit_flags(
        {"inherit_base_bonuses": False, "inherit_base_features": True}
    ) == (False, True)


def test_grants_from_entity_ignores_missing_key():
    assert grants_from_entity({}) == []
