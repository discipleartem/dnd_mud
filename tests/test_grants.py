"""Тесты grants, grant_mechanics и загрузки рас."""

import pytest

from core.grant_mechanics import (
    mechanics_from_grant_entry,
    normalize_armor_token,
    proficiency_tokens_from_grant,
)
from core.grants import grants_from_entity, inherit_flags
from core.races import (
    collect_race_grants,
    get_race_bonuses,
    load_races,
    resolve_subrace_id,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_load_races_catalog() -> None:
    races = load_races()
    assert len(races) > 0
    assert "id" in races[0]
    names = {race["id"]: race["name"] for race in load_races("en")}
    assert names["human"] == "Human"
    assert names["elf"] == "Elf"


def test_grants_from_entity() -> None:
    raw = {"type": "ability_increase", "count": 2, "amount": 1, "choice": True}
    grants = grants_from_entity({"grants": [raw]})
    assert grants[0] == raw
    assert grants[0] is not raw
    skill = grants_from_entity(
        {"grants": [{"type": "skill_proficiency", "skills": ["perception"]}]}
    )
    assert skill[0]["type"] == "skill_proficiency"
    assert grants_from_entity({}) == []


def test_human_race_bonuses_and_subrace() -> None:
    bonuses = get_race_bonuses("human", "standard")
    assert bonuses.get("strength") == 1
    assert bonuses.get("charisma") == 1
    assert resolve_subrace_id("human", None) == "standard"


def test_variant_human_grants_no_inherit() -> None:
    grants = collect_race_grants("human", "variant_human")
    types = [g.get("type") for g in grants]
    assert "ability_increase" in types
    assert "feat" in types
    assert "language" in types
    assert types.count("language") == 1


def test_inherit_flags_from_inherit_block() -> None:
    assert inherit_flags(
        {"inherit": {"ability_bonuses": False, "grants": False}}
    ) == (False, False)
    assert inherit_flags({}) == (True, True)


def test_normalize_armor_token_aliases() -> None:
    assert normalize_armor_token("light_armor") == "light"
    assert normalize_armor_token("shield") == "shield"


def test_mechanics_from_grant_entry() -> None:
    grant = {"type": "weapon_proficiency", "weapons": ["simple"]}
    assert mechanics_from_grant_entry(grant) == grant
    entry = {
        "type": "tool_proficiency",
        "mechanics": {"tools": ["thieves_tools"]},
    }
    mechanics = mechanics_from_grant_entry(entry)
    assert mechanics["type"] == "tool_proficiency"
    assert mechanics["tools"] == ["thieves_tools"]


def test_proficiency_tokens_from_weapon_grant() -> None:
    weapons, armors, tools = proficiency_tokens_from_grant(
        {"type": "weapon_proficiency", "weapons": ["martial"]}
    )
    assert weapons == ["martial"]
    assert armors == []
    assert tools == []
