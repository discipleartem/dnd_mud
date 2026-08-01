"""Общий golden-path контекст создания персонажа (variant human fighter)."""

from __future__ import annotations

from typing import Any

from core.character.models import Character
from core.mechanics.stats import STAT_NAMES
from core.types import CharacterClass

VARIANT_HUMAN_STATS: dict[str, int] = {
    "strength": 15,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 12,
    "wisdom": 10,
    "charisma": 8,
}


def flat_stats(value: int) -> dict[str, int]:
    """Одинаковое значение для всех характеристик PHB."""
    return dict.fromkeys(STAT_NAMES, value)


def minimal_character(**overrides: Any) -> Character:
    """Минимальный персонаж для UI smoke-тестов."""
    defaults: dict[str, Any] = {
        "name": "Hero",
        "race": "human",
        "class_id": CharacterClass.FIGHTER,
        "save_slug": "hero",
    }
    defaults.update(overrides)
    return Character(**defaults)


def fighter_acolyte_creation() -> dict[str, Any]:
    """Параметры создания: вариант человека, боец, прислужник."""
    return {
        "race_id": "human",
        "subrace_id": "variant_human",
        "class_id": "fighter",
        "subclass_id": "champion",
        "background_id": "acolyte",
        "level": 1,
        "stats": dict(VARIANT_HUMAN_STATS),
    }
