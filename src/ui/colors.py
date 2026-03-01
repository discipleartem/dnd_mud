"""Константы цветов для UI."""

from typing import Final

# Простые константы цветов (YAGNI - только необходимое)
RED: Final[str] = "RED"
GREEN: Final[str] = "GREEN"
CYAN: Final[str] = "CYAN"
WHITE: Final[str] = "WHITE"
BLUE: Final[str] = "BLUE"

# ANSI коды цветов (fallback если colorama недоступен)
FALLBACK_COLOR_MAP: Final[dict[str, str]] = {
    RED: "\033[31m",
    GREEN: "\033[32m",
    CYAN: "\033[36m",
    WHITE: "\033[37m",
    BLUE: "\033[34m",
}

# ANSI код для сброса цвета
ANSI_RESET: Final[str] = "\033[0m"
