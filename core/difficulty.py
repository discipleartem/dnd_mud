"""Проверки соответствия режима сложности игры.

Режим сложности задаётся при создании персонажа (Character.difficulty)
и проверяется при выборе приключений.
"""

from core.models import Adventure, Character


def adventure_requires_hardcore(adventure: Adventure) -> bool:
    """Приключение доступно только персонажам HardCore."""
    if adventure.hardcore_only:
        return True
    allowed = adventure.allowed_game_difficulties
    return (
        allowed is not None
        and "hardcore" in allowed
        and "normal" not in allowed
    )


def adventure_allows_difficulty(
    adventure: Adventure, game_difficulty: str
) -> bool:
    """Проверить, доступно ли приключение для режима персонажа.

    HardCore-персонаж не блокируется на приключениях без требования HardCore.
    """
    if not adventure_requires_hardcore(adventure):
        return True
    return game_difficulty == "hardcore"


def adventure_unavailable_reason(
    adventure: Adventure, character: Character
) -> str | None:
    """Ключ локализации причины недоступности или None, если доступно."""
    if character.level < adventure.min_level:
        return "adventures.unavailable_reason_level"
    if not adventure_allows_difficulty(adventure, character.difficulty):
        return "adventures.unavailable_reason_hardcore"
    return None
