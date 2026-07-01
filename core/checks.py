"""Проверки характеристик и спасброски (PHB)."""

import random
from typing import Any

from core.constants import proficiency_bonus
from core.dice import ability_modifier
from core.models import Character
from core.proficiency_checks import has_save_proficiency


def roll_d20(
    *,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, list[int]]:
    """Бросок к20 с преимуществом/помехой. Возвращает (итог, все броски)."""
    if advantage and disadvantage:
        advantage = False
        disadvantage = False
    if advantage or disadvantage:
        rolls = [random.randint(1, 20), random.randint(1, 20)]
        result = max(rolls) if advantage else min(rolls)
        return result, rolls
    roll = random.randint(1, 20)
    return roll, [roll]


def saving_throw_modifier(character: Character, ability_id: str) -> int:
    """Модификатор спасброска без броска к20."""
    score = int(character.stats.get(ability_id, 10))
    mod = ability_modifier(score)
    if has_save_proficiency(character.save_proficiencies, ability_id):
        mod += proficiency_bonus(character.level)
    return mod


def saving_throw(
    character: Character,
    ability_id: str,
    *,
    dc: int | None = None,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict[str, Any]:
    """Спасбросок по PHB: к20 + мод. характеристики [+ бонус мастерства]."""
    roll, rolls = roll_d20(advantage=advantage, disadvantage=disadvantage)
    modifier = saving_throw_modifier(character, ability_id)
    total = roll + modifier
    result: dict[str, Any] = {
        "ability": ability_id,
        "roll": roll,
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "proficient": has_save_proficiency(
            character.save_proficiencies, ability_id
        ),
    }
    if dc is not None:
        result["dc"] = dc
        result["success"] = total >= dc
    return result
