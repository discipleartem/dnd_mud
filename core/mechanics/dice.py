"""Броски кубиков для D&D 5e."""

import random

from core.constants import ability_modifier

__all__ = ["ability_modifier", "roll", "roll_ability_score"]


def roll(count: int = 1, sides: int = 20, modifier: int = 0) -> int:
    """Бросить несколько кубиков и сложить результат с модификатором.

    Args:
        count: Сколько кубиков бросить
        sides: Сколько граней у кубика
        modifier: Число, которое прибавляется к сумме

    Returns:
        Итоговая сумма
    """
    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total + modifier


def roll_ability_score() -> int:
    """Бросить 4d6 drop lowest для генерации характеристики.

    Returns:
        Сумма трёх лучших кубиков из четырёх
    """
    rolls = [roll(1, 6) for _ in range(4)]
    rolls.sort()
    return sum(rolls[1:])
