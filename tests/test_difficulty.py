"""Тесты проверок режима сложности."""

from core.difficulty import adventure_allows_difficulty
from core.models import Adventure


def test_adventure_allows_all_when_no_restrictions():
    adventure = Adventure(id="test", name="Test")

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is True


def test_adventure_hardcore_only():
    adventure = Adventure(id="hc", name="HC", hardcore_only=True)

    assert adventure_allows_difficulty(adventure, "hardcore") is True
    assert adventure_allows_difficulty(adventure, "normal") is False


def test_adventure_allowed_game_difficulties():
    adventure = Adventure(
        id="normal_only",
        name="Normal",
        allowed_game_difficulties=["normal"],
    )

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is False
