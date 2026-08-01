"""Константы D&D 5e из YAML."""

from typing import Any

from core.platform.catalog_loader import load_catalog
from core.platform.paths import CONSTANTS_FILE

MAX_CHARACTER_LEVEL = 10

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

EASY_START_LEVEL = 3

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STANDARD_ARRAY_MIN = min(STANDARD_ARRAY)
STANDARD_ARRAY_MAX = max(STANDARD_ARRAY)

POINT_BUY_BUDGET = 27
POINT_BUY_COSTS: dict[int, int] = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}
ABILITY_SCORE_MIN = 1
ABILITY_SCORE_DEFAULT = 10
ABILITY_SCORE_MAX = 20


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
