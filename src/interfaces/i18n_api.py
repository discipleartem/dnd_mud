"""API для системы интернационализации.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from abc import ABC, abstractmethod
from typing import Any

from entities.i18n import I18nConfig, LanguageInfo


class I18nLoader(ABC):
    """Интерфейс загрузчика переводов."""

    @abstractmethod
    def load_translations(self, language_code: str) -> dict[str, Any]:
        """Загрузить переводы для языка.

        Args:
            language_code: Код языка

        Returns:
            Словарь переводов
        """
        pass

    @abstractmethod
    def get_available_languages(self) -> dict[str, LanguageInfo]:
        """Получить доступные языки.

        Returns:
            Словарь языков
        """
        pass


class I18nDetector(ABC):
    """Интерфейс детектора языка системы."""

    @abstractmethod
    def detect_system_language(self) -> str | None:
        """Определить язык системы.

        Returns:
            Код языка или None если не удалось определить
        """
        pass


class I18nTranslator(ABC):
    """Интерфейс переводчика."""

    @abstractmethod
    def translate(
        self,
        key: str,
        context: str | None = None,
        language_code: str | None = None,
        **kwargs: Any
    ) -> str:
        """Перевести строку.

        Args:
            key: Ключ перевода
            context: Контекст перевода
            language_code: Код языка
            **kwargs: Дополнительные параметры для форматирования

        Returns:
            Переведенная строка
        """
        pass

    @abstractmethod
    def translate_plural(
        self,
        key: str,
        count: int,
        context: str | None = None,
        language_code: str | None = None,
        **kwargs: Any
    ) -> str:
        """Перевести строку с учетом множественного числа.

        Args:
            key: Ключ перевода
            count: Количество для определения формы
            context: Контекст перевода
            language_code: Код языка
            **kwargs: Дополнительные параметры

        Returns:
            Переведенная строка в правильной форме
        """
        pass

    @abstractmethod
    def set_language(self, language_code: str) -> bool:
        """Установить текущий язык.

        Args:
            language_code: Код языка

        Returns:
            True если язык установлен
        """
        pass

    @abstractmethod
    def get_current_language(self) -> str:
        """Получить текущий язык.

        Returns:
            Код текущего языка
        """
        pass


class I18nManager(ABC):
    """Интерфейс менеджера локализации."""

    @abstractmethod
    def initialize(self, config: I18nConfig) -> None:
        """Инициализировать систему i18n.

        Args:
            config: Конфигурация i18n
        """
        pass

    @abstractmethod
    def load_all_translations(self) -> None:
        """Загрузить все доступные переводы."""
        pass

    @abstractmethod
    def get_translator(self) -> I18nTranslator:
        """Получить интерфейс переводчика.

        Returns:
            Объект переводчика
        """
        pass

    @abstractmethod
    def reload_translations(self) -> None:
        """Перезагрузить все переводы."""
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """Получить статистику системы.

        Returns:
            Словарь со статистикой
        """
        pass


class I18nValidator(ABC):
    """Интерфейс валидатора переводов."""

    @abstractmethod
    def validate_translations(self, translations: dict[str, Any]) -> bool:
        """Валидировать структуру переводов.

        Args:
            translations: Словарь переводов

        Returns:
            True если структура валидна
        """
        pass

    @abstractmethod
    def find_missing_keys(
        self,
        base_translations: dict[str, Any],
        target_translations: dict[str, Any]
    ) -> list[str]:
        """Найти отсутствующие ключи.

        Args:
            base_translations: Базовые переводы
            target_translations: Целевые переводы

        Returns:
            Список отсутствующих ключей
        """
        pass
