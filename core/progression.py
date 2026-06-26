"""Прогрессия персонажа: опыт и уровни (PHB, макс. 10 уровень)."""

from core.classes import get_class_hit_dice
from core.dice import ability_modifier
from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.types import StatMap

XP_THRESHOLDS: list[int] = [
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
]


def level_from_xp(experience: int) -> int:
    """Уровень персонажа по накопленному опыту (1–MAX_CHARACTER_LEVEL)."""
    level = 1
    for idx, threshold in enumerate(XP_THRESHOLDS, start=1):
        if experience >= threshold:
            level = idx
    return min(level, MAX_CHARACTER_LEVEL)


def max_hp_for_level(class_id: str, stats: StatMap, level: int) -> int:
    """Максимум HP на заданном уровне (PHB average для 2+ уровней)."""
    level = clamp_level(level)
    hit_dice = get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    first = max(1, hit_dice + con_mod)
    if level <= 1:
        return first
    per_level = hit_dice // 2 + 1 + con_mod
    return first + per_level * (level - 1)


def apply_experience(character: Character, amount: int) -> Character:
    """Добавить опыт и пересчитать уровень и HP при повышении."""
    if amount <= 0:
        return character

    old_level = character.level
    new_xp = character.experience + amount
    new_level = level_from_xp(new_xp)
    new_max_hp = max_hp_for_level(
        character.class_name, character.stats, new_level
    )

    hp_gain = 0
    if new_level > old_level:
        hp_gain = new_max_hp - character.max_hp

    return Character(
        name=character.name,
        race=character.race,
        class_name=character.class_name,
        level=new_level,
        stats=character.stats,
        current_hp=character.current_hp + hp_gain,
        max_hp=new_max_hp,
        experience=new_xp,
        difficulty=character.difficulty,
        subrace=character.subrace,
        subclass_id=character.subclass_id,
        save_slug=character.save_slug,
        created_at=character.created_at,
    )
