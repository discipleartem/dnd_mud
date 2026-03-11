"""Адаптер для сервиса переводов.

Следует Clean Architecture - реализация интерфейса для работы с файлами переводов.
"""

from src.interfaces.services.translation_service_interface import TranslationService
from src.utils.translation_loader import TranslationLoader


class TranslationServiceAdapter(TranslationService):
    """Адаптер для работы с переводами через TranslationLoader.

    Следует принципу адаптера - преобразует интерфейс TranslationLoader
    в интерфейс TranslationService.
    """

    def __init__(self) -> None:
        """Инициализация адаптера."""
        self._loader = TranslationLoader()

    def get_translation(
        self, language_code: str, key: str, default: str
    ) -> str:
        """Получить перевод для указанного языка."""
        result = self._loader.get_translation(language_code, key, default)
        return result if result is not None else default

    def is_language_supported(self, language_code: str) -> bool:
        """Проверить, поддерживается ли язык."""
        return self._loader.is_language_supported(language_code)

    def get_supported_languages(self) -> list[str]:
        """Получить список поддерживаемых языков."""
        return self._loader.get_supported_languages()
