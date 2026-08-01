"""Правила движка по режиму сложности (Phase 2 hooks)."""

from core.types import GameDifficulty


def check_roll_flags(difficulty: GameDifficulty) -> tuple[bool, bool]:
    """Преимущество/помеха для проверок в сценарии по сложности."""
    if difficulty == "easy":
        return True, False
    if difficulty == "hardcore":
        return False, True
    return False, False
