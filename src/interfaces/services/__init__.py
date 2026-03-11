"""Интерфейсы сервисов.

Следует Clean Architecture - интерфейсы для внешних сервисов.
"""

from .translation_service_interface import TranslationService, TranslationError
from .ascii_art_service import AsciiArtService, AsciiArtError

__all__ = [
    'TranslationService',
    'TranslationError',
    'AsciiArtService', 
    'AsciiArtError'
]
