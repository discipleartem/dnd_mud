"""Отображение режима сложности."""

from colorama import Fore

from core.localization import get_string
from core.types import GameDifficulty, StringsDict


def _difficulty_label(strings: StringsDict, difficulty: GameDifficulty) -> str:
    """Локализованное название режима сложности."""
    mode_key = f"difficulty.{difficulty}"
    mode = get_string(strings, mode_key)
    if mode == mode_key:
        return difficulty
    return mode


def _difficulty_color(difficulty: GameDifficulty) -> str:
    """Цвет для отображения режима сложности."""
    match difficulty:
        case "easy":
            return str(Fore.GREEN)
        case "normal":
            return str(Fore.YELLOW)
        case "hardcore":
            return str(Fore.RED)
