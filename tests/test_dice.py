"""Тесты бросков кубиков и модификаторов."""

import random

import pytest

from core import dice


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
