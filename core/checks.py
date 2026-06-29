"""Проверки характеристик и навыков (PHB)."""

from typing import Literal

from core.abilities import ability_for_skill
from core.constants import proficiency_bonus
from core.dice import ability_modifier, roll
from core.models import Character
from core.proficiencies import get_class_saving_throws

Advantage = Literal["advantage", "disadvantage", "normal"]


def roll_d20(
    *,
    advantage: bool = False,
    disadvantage: bool = False,
) -> int:
    """Бросок к20 с преимуществом/помехой."""
    if advantage and disadvantage:
        return roll(1, 20)
    if advantage:
        return max(roll(1, 20), roll(1, 20))
    if disadvantage:
        return min(roll(1, 20), roll(1, 20))
    return roll(1, 20)


def ability_check_modifier(
    character: Character,
    ability: str,
    *,
    proficient: bool = False,
) -> int:
    """Модификатор проверки характеристики."""
    score = character.stats.get(ability, 10)
    mod = ability_modifier(int(score))
    if proficient:
        mod += proficiency_bonus(character.level)
    return mod


def skill_check_modifier(character: Character, skill_id: str) -> int:
    """Модификатор проверки навыка."""
    ability = ability_for_skill(skill_id)
    if ability is None:
        return 0
    proficient = skill_id in character.skills
    return ability_check_modifier(character, ability, proficient=proficient)


def saving_throw_modifier(character: Character, ability: str) -> int:
    """Модификатор спасброска."""
    proficient = ability in get_class_saving_throws(character.class_id)
    return ability_check_modifier(character, ability, proficient=proficient)


def passive_skill(character: Character, skill_id: str) -> int:
    """Пассивное значение навыка: 10 + модификаторы."""
    return 10 + skill_check_modifier(character, skill_id)


def ability_check(
    character: Character,
    ability: str,
    dc: int,
    *,
    proficient: bool = False,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, bool]:
    """Проверка характеристики. Возвращает (итог, успех)."""
    mod = ability_check_modifier(character, ability, proficient=proficient)
    total = roll_d20(advantage=advantage, disadvantage=disadvantage) + mod
    return total, total >= dc


def skill_check(
    character: Character,
    skill_id: str,
    dc: int,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, bool]:
    """Проверка навыка."""
    mod = skill_check_modifier(character, skill_id)
    total = roll_d20(advantage=advantage, disadvantage=disadvantage) + mod
    return total, total >= dc


def saving_throw(
    character: Character,
    ability: str,
    dc: int,
    *,
    advantage: bool = False,
    disadvantage: bool = False,
) -> tuple[int, bool]:
    """Спасбросок."""
    mod = saving_throw_modifier(character, ability)
    total = roll_d20(advantage=advantage, disadvantage=disadvantage) + mod
    return total, total >= dc
