"""Боевая подсистема (Phase 2 каркас)."""

import random
from typing import Any

__all__ = ["attack_roll", "roll_initiative"]


def roll_initiative(initiative_modifier: int) -> dict[str, Any]:
    """Бросок инициативы: к20 + модификатор."""
    roll = random.randint(1, 20)
    return {
        "roll": roll,
        "modifier": initiative_modifier,
        "total": roll + initiative_modifier,
    }


def attack_roll(
    attack_bonus: int,
    *,
    target_ac: int,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict[str, Any]:
    """Бросок атаки: к20 + бонус; сравнение с КБ."""
    if advantage and disadvantage:
        advantage = False
        disadvantage = False
    if advantage or disadvantage:
        rolls = [random.randint(1, 20), random.randint(1, 20)]
        roll = max(rolls) if advantage else min(rolls)
    else:
        rolls = [random.randint(1, 20)]
        roll = rolls[0]
    total = roll + attack_bonus
    return {
        "roll": roll,
        "rolls": rolls,
        "attack_bonus": attack_bonus,
        "total": total,
        "target_ac": target_ac,
        "hit": total >= target_ac,
        "critical": roll == 20,
    }
