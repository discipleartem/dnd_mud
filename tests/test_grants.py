"""Тесты нормализации grants и загрузки рас."""

from core.grants import (
    grants_from_entity,
    inherit_flags,
)
from core.races import (
    clear_races_cache,
    collect_race_grants,
    get_race_bonuses,
    load_races,
    resolve_subrace_id,
)


def test_load_races_returns_non_empty_list() -> None:
    races = load_races()
    assert len(races) > 0
    assert "id" in races[0]
    assert "name" in races[0]


def test_load_races_returns_english_names() -> None:
    races = load_races("en")
    names = {race["id"]: race["name"] for race in races}
    assert names["human"] == "Human"
    assert names["elf"] == "Elf"


def test_grants_from_entity_copies_dict():
    raw = {"type": "ability_increase", "count": 2, "amount": 1, "choice": True}
    grants = grants_from_entity({"grants": [raw]})
    assert grants[0] == raw
    assert grants[0] is not raw


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


def test_inherit_flags_from_inherit_block():
    assert inherit_flags(
        {"inherit": {"ability_bonuses": False, "grants": False}}
    ) == (False, False)
    assert inherit_flags({}) == (True, True)


def test_grants_from_entity_ignores_missing_key():
    assert grants_from_entity({}) == []
