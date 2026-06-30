"""Тесты бросков кубиков и модификаторов."""

import random

from core import dice


def test_ability_modifier_table():
    """Модификатор характеристики: (значение - 10) // 2."""
    assert dice.ability_modifier(8) == -1
    assert dice.ability_modifier(10) == 0
    assert dice.ability_modifier(12) == 1
    assert dice.ability_modifier(18) == 4


def test_roll_sums_dice_and_modifier(monkeypatch):
    """roll суммирует броски и модификатор."""
    values = iter([3, 5])
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(values))

    assert dice.roll(count=2, sides=6, modifier=2) == 10


def test_roll_ability_score_drops_lowest(monkeypatch):
    """4d6 drop lowest: сумма трёх лучших кубиков."""
    values = iter([1, 6, 5, 4])

    def fake_roll(*args: object, **kwargs: object) -> int:
        return next(values)

    monkeypatch.setattr(dice, "roll", fake_roll)

    assert dice.roll_ability_score() == 15
