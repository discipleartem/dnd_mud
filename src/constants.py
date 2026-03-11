"""Общие константы проекта.

Следует DRY - одна константа на весь проект.
"""

from typing import Final

# Языковые константы
SUPPORTED_LANGUAGES: Final[set[str]] = {"ru", "en"}
DEFAULT_LANGUAGE: Final[str] = "ru"

# Ограничения длины текста
MAX_TITLE_LENGTH: Final[int] = 100
MAX_SUBTITLE_LENGTH: Final[int] = 200
MAX_DESCRIPTION_LENGTH: Final[int] = 500
MAX_ASCII_ART_LENGTH: Final[int] = 2000

# Значения по умолчанию для контента
DEFAULT_TITLE: Final[str] = "Добро пожаловать в D&D MUD"
DEFAULT_SUBTITLE: Final[str] = (
    "Текстовая игра по мотивам Dungeons & Dragons 5e"
)
DEFAULT_DESCRIPTION: Final[str] = (
    "Приготовьтесь к эпическому приключению в мире фэнтези!"
)
DEFAULT_PRESS_ENTER: Final[str] = "Нажмите Enter для продолжения..."
