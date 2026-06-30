"""Тесты генерации характеристик, кубиков и констант PHB."""

import random

import pytest

from core import dice
from core.constants import difficulty_class, proficiency_bonus
from core.stats import (
    POINT_BUY_BUDGET,
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


def test_difficulty_class_medium() -> None:
    assert difficulty_class("medium") == 10


def test_ability_modifier_and_rolls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Модификатор, roll и 4d6 drop lowest."""
    assert dice.ability_modifier(8) == -1
    assert dice.ability_modifier(10) == 0
    assert dice.ability_modifier(18) == 4

    values = iter([3, 5])
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(values))
    assert dice.roll(count=2, sides=6, modifier=2) == 10

    roll_values = iter([1, 6, 5, 4])

    def fake_roll(*args: object, **kwargs: object) -> int:
        return next(roll_values)

    monkeypatch.setattr(dice, "roll", fake_roll)
    assert dice.roll_ability_score() == 15


def test_validate_point_buy_finish_accepts_full_budget() -> None:
    values = [15, 14, 13, 12, 10, 8]
    assert validate_point_buy_finish(values) is None
    assert point_buy_points_remaining(values) == 0


def test_validate_point_buy_finish_rejects_unspent_points() -> None:
    values = [8, 8, 8, 8, 8, 8]
    assert (
        validate_point_buy_finish(values) == "character.stats_points_unspent"
    )
    assert point_buy_points_remaining(values) == POINT_BUY_BUDGET


def test_validate_point_buy_finish_rejects_overspent_budget() -> None:
    values = [15, 15, 15, 15, 15, 15]
    assert (
        validate_point_buy_finish(values) == "character.stats_points_overspent"
    )
    assert point_buy_points_remaining(values) < 0


def test_point_buy_points_remaining_matches_stat_names_length() -> None:
    values = [10, 10, 10, 10, 10, 10]
    assert len(values) == len(STAT_NAMES)
    assert point_buy_points_remaining(values) == POINT_BUY_BUDGET - 12
