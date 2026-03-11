"""Интерфейсы сервисов.

Следует Clean Architecture - интерфейсы для внешних сервисов.
"""

from .ascii_art_service import AsciiArtError, AsciiArtService
from .translation_service_interface import TranslationError, TranslationService

__all__ = [
    "TranslationService",
    "TranslationError",
    "AsciiArtService",
    "AsciiArtError",
]
