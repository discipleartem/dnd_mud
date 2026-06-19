"""Проверки соответствия режима сложности игры.

Режим сложности задаётся при создании персонажа (Character.difficulty)
и проверяется при выборе приключений и модов.
"""

from typing import Any

from core.models import Adventure

VALID_GAME_DIFFICULTIES = ("normal", "hardcore")


def adventure_allows_difficulty(
    adventure: Adventure, game_difficulty: str
) -> bool:
    """Проверить, доступно ли приключение для режима персонажа."""
    if adventure.hardcore_only and game_difficulty != "hardcore":
        return False
    allowed = adventure.allowed_game_difficulties
    if allowed is None:
        return True
    return game_difficulty in allowed


def mod_allows_difficulty(
    mod_meta: dict[str, Any], game_difficulty: str
) -> bool:
    """Проверить, доступен ли мод для режима персонажа."""
    required = mod_meta.get("requires_game_difficulty")
    if required is None:
        return True
    return game_difficulty == str(required)
