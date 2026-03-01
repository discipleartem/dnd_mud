"""Сущность интернационализации (i18n).

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class I18nConfig:
    """Конфигурация системы i18n."""

    default_language: str = "ru"
    fallback_language: str = "en"
    cache_enabled: bool = True
    auto_detect_language: bool = True


@dataclass
class LanguageInfo:
    """Информация о языке."""

    code: str
    name: str
    native_name: str
    rtl: bool = False  # справа налево


@dataclass
class TranslationKey:
    """Ключ перевода с контекстом."""

    key: str
    context: str | None = None
    plural: bool = False
    count: int | None = None

    def get_full_key(self) -> str:
        """Получить полный ключ с контекстом."""
        if self.context:
            return f"{self.context}.{self.key}"
        return self.key


class I18n:
    """Основная сущность системы интернационализации.

    Предоставляет базовый функционал для работы с переводами.
    """

    def __init__(self, config: I18nConfig) -> None:
        """Инициализация i18n."""
        self._config = config
        self._current_language: str = config.default_language
        self._translations: dict[str, dict[str, Any]] = {}
        self._cache: dict[str, str] = {}
        self._languages: dict[str, LanguageInfo] = {}

        # Базовые языки
        self._init_default_languages()

    def _init_default_languages(self) -> None:
        """Инициализировать языки по умолчанию."""
        self._languages = {
            "ru": LanguageInfo("ru", "Russian", "Русский"),
            "en": LanguageInfo("en", "English", "English"),
        }

    @property
    def current_language(self) -> str:
        """Текущий язык."""
        return self._current_language

    @property
    def config(self) -> I18nConfig:
        """Конфигурация."""
        return self._config

    def set_language(self, language_code: str) -> bool:
        """Установить текущий язык.

        Args:
            language_code: Код языка

        Returns:
            True если язык установлен, False если язык не найден
        """
        if language_code in self._languages:
            self._current_language = language_code
            if self._config.cache_enabled:
                self._cache.clear()
            return True
        return False

    def add_language(self, language_info: LanguageInfo) -> None:
        """Добавить новый язык."""
        self._languages[language_info.code] = language_info

    def get_available_languages(self) -> dict[str, LanguageInfo]:
        """Получить доступные языки."""
        return self._languages.copy()

    def load_translations(self, language_code: str, translations: dict[str, Any]) -> None:
        """Загрузить переводы для языка.

        Args:
            language_code: Код языка
            translations: Словарь переводов
        """
        self._translations[language_code] = translations
        if self._config.cache_enabled:
            self._cache.clear()

    def get_translation(
        self,
        key: TranslationKey,
        language_code: str | None = None
    ) -> str:
        """Получить перевод по ключу.

        Args:
            key: Ключ перевода
            language_code: Код языка (если None, используется текущий)

        Returns:
            Переведенная строка или ключ если перевод не найден
        """
        lang = language_code or self._current_language
        full_key = key.get_full_key()

        # Проверяем кэш
        if self._config.cache_enabled and full_key in self._cache:
            return self._cache[full_key]

        # Ищем перевод
        translation = self._find_translation(full_key, lang)

        # Кэшируем результат
        if self._config.cache_enabled and translation:
            self._cache[full_key] = translation

        return translation or full_key

    def _find_translation(self, key: str, language_code: str) -> str | None:
        """Найти перевод в иерархии языков."""
        # Сначала ищем в текущем языке
        if language_code in self._translations:
            translation = self._get_nested_value(
                self._translations[language_code], key
            )
            if translation:
                return str(translation)

        # Если не нашли, пробуем язык по умолчанию
        if (language_code != self._config.fallback_language and
            self._config.fallback_language in self._translations):
            translation = self._get_nested_value(
                self._translations[self._config.fallback_language], key
            )
            if translation:
                return str(translation)

        return None

    def _get_nested_value(self, data: dict[str, Any], key: str) -> Any:
        """Получить значение из вложенного словаря по точечному ключу."""
        keys = key.split('.')
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current

    def clear_cache(self) -> None:
        """Очистить кэш переводов."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Получить статистику кэша."""
        return {
            "size": len(self._cache),
            "languages": len(self._translations),
            "available_languages": len(self._languages),
        }
