"""Прогрессия персонажа: опыт и уровни (PHB, макс. 10 уровень)."""

from dataclasses import replace

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


def roll_hp_gain_for_level_up(
    class_id: str,
    stats: StatMap,
    new_level: int,
    difficulty: GameDifficulty,
) -> tuple[int, int | None]:
    """Прирост HP за повышение до new_level.

    Для HardCore возвращает также значение броска кости.
    """
    hit_dice = get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    if difficulty == "hardcore":
        dice = roll(1, hit_dice)
        return dice + con_mod, dice
    return hp_gain_for_level(new_level, hit_dice, con_mod, difficulty), None


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


def grant_experience(character: Character, amount: int) -> Character:
    """Добавить опыт без повышения уровня."""
    if amount <= 0:
        return character
    return replace(character, experience=character.experience + amount)


def has_pending_level_up(character: Character) -> bool:
    """Есть ли неприменённое повышение уровня по текущему XP."""
    if character.level >= MAX_CHARACTER_LEVEL:
        return False
    return character.level < level_from_xp(character.experience)


def apply_level_up(character: Character, hp_gain: int) -> Character:
    """Повысить персонажа на один уровень с заданным приростом HP."""
    if not has_pending_level_up(character):
        return character
    new_level = character.level + 1
    return replace(
        character,
        level=new_level,
        max_hp=character.max_hp + hp_gain,
        current_hp=character.current_hp + hp_gain,
    )


def resolve_pending_level_ups(character: Character) -> Character:
    """Применить все ожидающие повышения без UI.

    Для тестов и apply_experience.
    """
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        gain, _ = roll_hp_gain_for_level_up(
            char.class_name,
            char.stats,
            new_level,
            char.difficulty,
        )
        char = apply_level_up(char, gain)
    return char


def apply_experience(character: Character, amount: int) -> Character:
    """Добавить опыт и сразу применить все повышения уровня (без UI)."""
    return resolve_pending_level_ups(grant_experience(character, amount))
