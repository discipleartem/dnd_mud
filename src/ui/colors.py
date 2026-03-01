"""Константы цветов для UI."""

from enum import StrEnum
from typing import Final


class ColorName(StrEnum):
    """Имена доступных цветов."""
    RED = "RED"
    GREEN = "GREEN"
    CYAN = "CYAN"
    WHITE = "WHITE"
    BLUE = "BLUE"


# ANSI коды цветов (fallback если colorama недоступен)
FALLBACK_COLOR_MAP: Final[dict[str, str]] = {
    ColorName.RED: "\033[31m",
    ColorName.GREEN: "\033[32m",
    ColorName.CYAN: "\033[36m",
    ColorName.WHITE: "\033[37m",
    ColorName.BLUE: "\033[34m",
}

# ANSI код для сброса цвета
ANSI_RESET: Final[str] = "\033[0m"
