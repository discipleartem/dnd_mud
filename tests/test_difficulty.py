"""Тесты проверок режима сложности."""

from core.difficulty import (
    adventure_allows_difficulty,
    adventure_requires_hardcore,
    adventure_unavailable_reason,
)
from core.models import Adventure, Character


def test_adventure_allows_all_when_no_restrictions():
    adventure = Adventure(id="test", name="Test")

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is True


def test_adventure_hardcore_only():
    adventure = Adventure(id="hc", name="HC", hardcore_only=True)

    assert adventure_allows_difficulty(adventure, "hardcore") is True
    assert adventure_allows_difficulty(adventure, "normal") is False


def test_hardcore_character_allowed_on_normal_adventure():
    """HardCore-персонаж доступен на приключениях без требования HardCore."""
    adventure = Adventure(
        id="normal_only",
        name="Normal",
        allowed_game_difficulties=["normal"],
    )

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is True


def test_adventure_requires_hardcore_from_allowed_list():
    adventure = Adventure(
        id="hc_list",
        name="HC",
        allowed_game_difficulties=["hardcore"],
    )

    assert adventure_requires_hardcore(adventure) is True
    assert adventure_allows_difficulty(adventure, "hardcore") is True
    assert adventure_allows_difficulty(adventure, "normal") is False


def test_adventure_unavailable_reason_level():
    adventure = Adventure(id="high", name="High", min_level=5)
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=1,
    )

    assert (
        adventure_unavailable_reason(adventure, character)
        == "adventures.unavailable_reason_level"
    )


def test_adventure_unavailable_reason_hardcore():
    adventure = Adventure(id="hc", name="HC", hardcore_only=True)
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )

    assert (
        adventure_unavailable_reason(adventure, character)
        == "adventures.unavailable_reason_hardcore"
    )
