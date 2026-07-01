"""Тесты спасбросков класса."""

import pytest

from core.character_builder import resolve_creation_grants
from core.checks import saving_throw_modifier
from core.models import Character
from core.proficiency_checks import get_class_saving_throws

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


@pytest.mark.parametrize(
    ("class_id", "expected"),
    [
        ("fighter", ["strength", "constitution"]),
        ("rogue", ["dexterity", "intelligence"]),
        ("cleric", ["wisdom", "charisma"]),
        ("bard", ["dexterity", "charisma"]),
    ],
)
def test_class_saving_throws_yaml(class_id: str, expected: list[str]) -> None:
    assert get_class_saving_throws(class_id) == expected


def test_resolve_creation_grants_includes_saves() -> None:
    grants = resolve_creation_grants(
        "human",
        "standard",
        "fighter",
        None,
        None,
        1,
    )
    assert "strength" in grants.save_ids
    assert "constitution" in grants.save_ids


def test_saving_throw_modifier_with_proficiency() -> None:
    char = Character(
        name="Test",
        race="human",
        class_id="fighter",
        stats={"strength": 16, "dexterity": 10, "constitution": 14},
        save_proficiencies=["strength"],
        level=1,
    )
    assert saving_throw_modifier(char, "strength") == 5
    assert saving_throw_modifier(char, "dexterity") == 0
