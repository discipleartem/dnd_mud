"""Константы D&D 5e из YAML."""

from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog

CONSTANTS_FILE = Path("database/core/constants.yaml")

MAX_CHARACTER_LEVEL = 10


def clamp_level(level: int) -> int:
    """Ограничить уровень диапазоном 1–MAX_CHARACTER_LEVEL."""
    return max(1, min(level, MAX_CHARACTER_LEVEL))


ABILITY_MODIFIER_SCORE_MIN = 1
ABILITY_MODIFIER_SCORE_MAX = 30

# Fallback если YAML недоступен
_DEFAULT_PROFICIENCY_BONUS: dict[int, int] = {
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 3,
    8: 3,
    9: 4,
    10: 4,
    11: 4,
    12: 4,
    13: 5,
    14: 5,
    15: 5,
    16: 5,
    17: 6,
    18: 6,
    19: 6,
    20: 6,
}


def _load_constants() -> dict[str, Any]:
    """Загрузить блок constants из YAML."""
    return load_catalog(CONSTANTS_FILE, "constants")


def proficiency_bonus(level: int) -> int:
    """Бонус мастерства по уровню персонажа (PHB)."""
    level = clamp_level(level)
    raw = _load_constants().get("proficiency_bonus", {})
    if isinstance(raw, dict):
        value = raw.get(level)
        if isinstance(value, int):
            return value
    return _DEFAULT_PROFICIENCY_BONUS.get(level, 2)


def difficulty_class(tier: str) -> int:
    """Сл по имени tier (easy, medium, hard, …)."""
    raw = _load_constants().get("difficulty_classes", {})
    if isinstance(raw, dict):
        value = raw.get(tier)
        if isinstance(value, int):
            return value
    defaults = {
        "trivial": 0,
        "easy": 5,
        "medium": 10,
        "hard": 15,
        "very_hard": 20,
        "nearly_impossible": 25,
        "impossible": 30,
    }
    return defaults.get(tier, 10)


def ability_modifier(score: int) -> int:
    """Модификатор характеристики (PHB): таблица из YAML, clamp 1–30."""
    clamped = max(
        ABILITY_MODIFIER_SCORE_MIN,
        min(ABILITY_MODIFIER_SCORE_MAX, int(score)),
    )
    raw = _load_constants().get("ability_modifiers", {})
    if isinstance(raw, dict):
        value = raw.get(clamped)
        if value is None:
            value = raw.get(str(clamped))
        if isinstance(value, int):
            return value
    return (clamped - 10) // 2
