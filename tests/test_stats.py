"""Тесты кубиков, констант PHB, point-buy и сложности приключений."""

import random

import pytest

from core import dice
from core.constants import difficulty_class, proficiency_bonus
from core.difficulty import (
    adventure_allows_difficulty,
    adventure_requires_hardcore,
    adventure_unavailable_reason,
)
from core.models import Adventure, Character
from core.stats import (
    STAT_NAMES,
    point_buy_points_remaining,
    validate_point_buy_finish,
)


@pytest.mark.parametrize(
    "level,expected_bonus",
    [(1, 2), (5, 3)],
)
def test_proficiency_bonus(level: int, expected_bonus: int) -> None:
    assert proficiency_bonus(level) == expected_bonus


def test_difficulty_class_and_dice(monkeypatch: pytest.MonkeyPatch) -> None:
    assert difficulty_class("medium") == 10
    assert dice.ability_modifier(18) == 4
    values = iter([3, 5])
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(values))
    assert dice.roll(count=2, sides=6, modifier=2) == 10


def test_point_buy_validation() -> None:
    full = [15, 14, 13, 12, 10, 8]
    assert validate_point_buy_finish(full) is None
    assert point_buy_points_remaining(full) == 0
    low = [8, 8, 8, 8, 8, 8]
    assert validate_point_buy_finish(low) == "character.stats_points_unspent"
    assert len(low) == len(STAT_NAMES)


def test_adventure_difficulty_rules() -> None:
    open_adv = Adventure(id="test", name="Test")
    assert adventure_allows_difficulty(open_adv, "normal") is True
    hc = Adventure(id="hc", name="HC", hardcore_only=True)
    assert adventure_allows_difficulty(hc, "hardcore") is True
    assert adventure_allows_difficulty(hc, "normal") is False
    hc_list = Adventure(
        id="hc_list",
        name="HC",
        allowed_game_difficulties=["hardcore"],
    )
    assert adventure_requires_hardcore(hc_list) is True


def test_adventure_unavailable_reason() -> None:
    high = Adventure(id="high", name="High", min_level=5)
    char = Character(name="Hero", race="human", class_id="fighter", level=1)
    assert (
        adventure_unavailable_reason(high, char)
        == "adventures.unavailable_reason_level"
    )
    hc = Adventure(id="hc", name="HC", hardcore_only=True)
    normal_char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    assert (
        adventure_unavailable_reason(hc, normal_char)
        == "adventures.unavailable_reason_hardcore"
    )
