"""Опыт и пороги уровней (PHB, макс. 10 уровень)."""

from dataclasses import replace

from core.levels import MAX_CHARACTER_LEVEL, clamp_level
from core.models import Character

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


def xp_for_level(level: int) -> int:
    """Минимальный накопленный опыт PHB для достижения уровня.

    Используется при создании персонажа. В игре опыт только растёт
    (`grant_experience`); после левелапа избыток над порогом сохраняется.
    """
    level = clamp_level(level)
    return XP_THRESHOLDS[level - 1]


def xp_covers_level(experience: int, level: int) -> bool:
    """Достаточно ли опыта для текущего уровня (>= минимального порога)."""
    return experience >= xp_for_level(level)


def grant_experience(character: Character, amount: int) -> Character:
    """Добавить опыт без повышения уровня (накопительно, без обрезки)."""
    if amount <= 0:
        return character
    return replace(character, experience=character.experience + amount)


def has_pending_level_up(character: Character) -> bool:
    """Есть ли неприменённое повышение уровня по текущему XP."""
    if character.level >= MAX_CHARACTER_LEVEL:
        return False
    return character.level < level_from_xp(character.experience)
