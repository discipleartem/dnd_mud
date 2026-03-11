"""Интерфейсы для D&D MUD проекта.

Следует Clean Architecture - интерфейсы определяют контракты между слоями.
"""

# Импорты из подпапок
from .services.ascii_art_service import AsciiArtError, AsciiArtService
from .services.translation_service_interface import (
    TranslationError,
    TranslationService,
)

__all__ = [
    "TranslationService",
    "TranslationError",
    "AsciiArtService",
    "AsciiArtError",
]
