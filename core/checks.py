"""Проверки характеристик и спасброски (PHB)."""

import random
from typing import Any

from core.abilities import ability_for_skill
from core.constants import ability_modifier, proficiency_bonus
from core.models import Character
from core.proficiencies.proficiency_checks import has_save_proficiency
from core.stats import ABILITY_SCORE_DEFAULT


def _skill_ability_id(skill_id: str) -> str:
    ability_id = ability_for_skill(skill_id)
    return ability_id if ability_id is not None else "dexterity"


def _has_skill_proficiency(character: Character, skill_id: str) -> bool:
    return skill_id in character.skills


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
    score = int(character.stats.get(ability_id, ABILITY_SCORE_DEFAULT))
    mod = ability_modifier(score)
    if has_save_proficiency(character.save_proficiencies, ability_id):
        mod += proficiency_bonus(character.level)
    return mod


def ability_modifier_for_character(
    character: Character, ability_id: str
) -> int:
    """Модификатор характеристики персонажа."""
    score = int(character.stats.get(ability_id, ABILITY_SCORE_DEFAULT))
    return ability_modifier(score)


def ability_check(
    character: Character,
    ability_id: str,
    *,
    dc: int | None = None,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict[str, Any]:
    """Проверка характеристики: к20 + модификатор."""
    roll, rolls = roll_d20(advantage=advantage, disadvantage=disadvantage)
    modifier = ability_modifier_for_character(character, ability_id)
    total = roll + modifier
    result: dict[str, Any] = {
        "ability": ability_id,
        "roll": roll,
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
    }
    if dc is not None:
        result["dc"] = dc
        result["success"] = total >= dc
    return result


def skill_check(
    character: Character,
    skill_id: str,
    *,
    dc: int | None = None,
    advantage: bool = False,
    disadvantage: bool = False,
) -> dict[str, Any]:
    """Проверка навыка: к20 + мод. характеристики [+ бонус мастерства]."""
    ability_id = _skill_ability_id(skill_id)
    roll, rolls = roll_d20(advantage=advantage, disadvantage=disadvantage)
    modifier = ability_modifier_for_character(character, ability_id)
    proficient = _has_skill_proficiency(character, skill_id)
    if proficient:
        modifier += proficiency_bonus(character.level)
    total = roll + modifier
    result: dict[str, Any] = {
        "skill": skill_id,
        "ability": ability_id,
        "roll": roll,
        "rolls": rolls,
        "modifier": modifier,
        "total": total,
        "proficient": proficient,
    }
    if dc is not None:
        result["dc"] = dc
        result["success"] = total >= dc
    return result


def passive_skill(character: Character, skill_id: str) -> int:
    """Пассивное значение навыка: 10 + модификатор проверки."""
    ability_id = _skill_ability_id(skill_id)
    modifier = ability_modifier_for_character(character, ability_id)
    if _has_skill_proficiency(character, skill_id):
        modifier += proficiency_bonus(character.level)
    return 10 + modifier


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
