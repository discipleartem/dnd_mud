"""Константы и ограничения уровня персонажа."""

MAX_CHARACTER_LEVEL = 10


def clamp_level(level: int) -> int:
    """Ограничить уровень диапазоном 1–MAX_CHARACTER_LEVEL."""
    return max(1, min(level, MAX_CHARACTER_LEVEL))
