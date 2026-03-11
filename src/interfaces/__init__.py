"""Интерфейсы для D&D MUD проекта.

Следует Clean Architecture - интерфейсы определяют контракты между слоями.
"""

# Импорты из подпапок
from .services.translation_service_interface import TranslationService, TranslationError
from .services.ascii_art_service import AsciiArtService, AsciiArtError

__all__ = [
    'TranslationService',
    'TranslationError', 
    'AsciiArtService',
    'AsciiArtError'
]
