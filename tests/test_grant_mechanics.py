"""Тесты core.grant_mechanics."""

from core.grant_mechanics import (
    mechanics_from_grant_entry,
    normalize_armor_token,
    proficiency_tokens_from_grant,
)


def test_normalize_armor_token_aliases() -> None:
    assert normalize_armor_token("light_armor") == "light"
    assert normalize_armor_token("shield") == "shield"


def test_mechanics_from_grant_entry_flat_grant() -> None:
    grant = {"type": "weapon_proficiency", "weapons": ["simple"]}
    assert mechanics_from_grant_entry(grant) == grant


def test_mechanics_from_grant_entry_class_feature() -> None:
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
