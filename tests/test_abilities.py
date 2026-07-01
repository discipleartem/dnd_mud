"""Тесты core.abilities."""

from core.abilities import ability_ids, skill_ids


def test_skill_ids_non_empty() -> None:
    ids = skill_ids()
    assert len(ids) >= 18
    assert "athletics" in ids
    assert "perception" in ids


def test_ability_ids_non_empty() -> None:
    ids = ability_ids()
    assert len(ids) == 6
    assert "strength" in ids
    assert "charisma" in ids
