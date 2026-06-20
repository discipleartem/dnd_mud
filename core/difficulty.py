"""Проверки соответствия режима сложности игры.

Режим сложности задаётся при создании персонажа (Character.difficulty)
и проверяется при выборе приключений.
"""

from core.models import Adventure


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
