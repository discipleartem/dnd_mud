"""Опыт и уровни персонажа."""

from dataclasses import replace

from core.character.models import Character
from core.constants import (
    EASY_START_LEVEL,
    MAX_CHARACTER_LEVEL,
    XP_THRESHOLDS,
    clamp_level,
)

ASI_FEATURE_ID = "ability_score_improvement"

__all__ = [
    "ASI_FEATURE_ID",
    "EASY_START_LEVEL",
    "XP_THRESHOLDS",
    "grant_experience",
    "has_pending_level_up",
    "level_from_xp",
    "xp_covers_level",
    "xp_for_level",
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
