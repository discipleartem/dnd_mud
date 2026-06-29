"""Константы D&D 5e из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml
from core.levels import clamp_level

CONSTANTS_FILE = Path("database/core/constants.yaml")

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


@lru_cache(maxsize=1)
def _load_constants() -> dict[str, Any]:
    """Загрузить блок constants из YAML."""
    data = load_yaml(CONSTANTS_FILE)
    constants = data.get("constants", {})
    if isinstance(constants, dict):
        return constants
    return {}


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


def cover_bonus(tier: str) -> int | str | None:
    """Бонус укрытия к КД или описание полного укрытия."""
    raw = _load_constants().get("situational_modifiers", {})
    if not isinstance(raw, dict):
        return None
    cover = raw.get("cover", {})
    if isinstance(cover, dict):
        return cover.get(tier)
    return None


def size_label(size_id: str) -> str:
    """Читаемое название размера."""
    raw = _load_constants().get("sizes", {})
    if isinstance(raw, dict):
        label = raw.get(size_id)
        if isinstance(label, str):
            return label
    return size_id
