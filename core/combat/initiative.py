"""Инициатива (PHB) — каркас Phase 2."""

import random
from typing import Any


def roll_initiative(initiative_modifier: int) -> dict[str, Any]:
    """Бросок инициативы: к20 + модификатор."""
    roll = random.randint(1, 20)
    return {
        "roll": roll,
        "modifier": initiative_modifier,
        "total": roll + initiative_modifier,
    }
