"""Прогрессия персонажа: опыт и уровни (PHB, макс. 10 уровень)."""

from core.classes import get_class_hit_dice
from core.dice import ability_modifier, roll
from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character
from core.types import GameDifficulty, StatMap

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


def hp_gain_for_level(
    level: int,
    hit_dice: int,
    con_mod: int,
    difficulty: GameDifficulty = "normal",
) -> int:
    """Прирост максимальных HP за один уровень класса."""
    if difficulty == "hardcore":
        return roll(1, hit_dice) + con_mod
    if level <= 1:
        return max(1, hit_dice + con_mod)
    return hit_dice // 2 + 1 + con_mod


def max_hp_for_level(
    class_id: str,
    stats: StatMap,
    level: int,
    difficulty: GameDifficulty = "normal",
) -> int:
    """Максимум HP на заданном уровне с учётом режима сложности."""
    level = clamp_level(level)
    hit_dice = get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    total = 0
    for lvl in range(1, level + 1):
        total += hp_gain_for_level(lvl, hit_dice, con_mod, difficulty)
    return total


def apply_experience(character: Character, amount: int) -> Character:
    """Добавить опыт и пересчитать уровень и HP при повышении."""
    if amount <= 0:
        return character

    old_level = character.level
    new_xp = character.experience + amount
    new_level = level_from_xp(new_xp)

    hp_gain = 0
    if new_level > old_level:
        if character.difficulty == "hardcore":
            hit_dice = get_class_hit_dice(character.class_name)
            con_mod = ability_modifier(character.stats.get("constitution", 10))
            for lvl in range(old_level + 1, new_level + 1):
                hp_gain += hp_gain_for_level(
                    lvl, hit_dice, con_mod, "hardcore"
                )
            new_max_hp = character.max_hp + hp_gain
        else:
            new_max_hp = max_hp_for_level(
                character.class_name,
                character.stats,
                new_level,
                character.difficulty,
            )
            hp_gain = new_max_hp - character.max_hp
    else:
        new_max_hp = character.max_hp

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
