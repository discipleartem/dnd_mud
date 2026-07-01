"""Общий golden-path контекст создания персонажа (variant human fighter)."""

from __future__ import annotations

from typing import Any

VARIANT_HUMAN_STATS: dict[str, int] = {
    "strength": 15,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 12,
    "wisdom": 10,
    "charisma": 8,
}


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
