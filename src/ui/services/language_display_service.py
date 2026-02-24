"""Сервисы для отображения информации о языках."""

from typing import TYPE_CHECKING, Any

from i18n import t


def _safe_str(value: Any) -> str:
    """Безопасно преобразовать значение в строку.

    Args:
        value: Значение для преобразования

    Returns:
        Строковое представление значения
    """
    return value if isinstance(value, str) else str(value)


if TYPE_CHECKING:
    from src.services.language_service import Language


class LanguageDisplayService:
    """Сервис для отображения информации о языках в UI."""

    @staticmethod
    def get_language_name(language: "Language") -> str:
        """Получить локализованное название языка.

        Args:
            language: Объект языка

        Returns:
            Локализованное название языка или код, если перевод не найден.
        """
        if language.localization_keys.get("name"):
            name = t(language.localization_keys["name"])
            return _safe_str(name)
        fallback_name = language.fallback_data.get("name", language.code)
        return _safe_str(fallback_name)

    @staticmethod
    def get_language_description(language: "Language") -> str:
        """Получить локализованное описание языка.

        Args:
            language: Объект языка

        Returns:
            Локализованное описание языка или пустая строка.
        """
        if language.localization_keys.get("description"):
            desc = t(language.localization_keys["description"])
            return _safe_str(desc)
        fallback_desc = language.fallback_data.get("description", "")
        return _safe_str(fallback_desc)

    @staticmethod
    def get_language_speakers(language: "Language") -> str:
        """Получить локализованный список носителей языка.

        Args:
            language: Объект языка

        Returns:
            Локализованный список носителей или пустая строка.
        """
        if language.localization_keys.get("speakers"):
            speakers = t(language.localization_keys["speakers"])
            return _safe_str(speakers)
        fallback_speakers = language.fallback_data.get("speakers", "")
        return _safe_str(fallback_speakers)

    @staticmethod
    def get_language_type_name(language: "Language") -> str:
        """Получить локализованное название типа языка.

        Args:
            language: Объект языка

        Returns:
            Локализованное название типа языка.
        """
        type_name = t(f"language.types.{language.type}")
        return _safe_str(type_name)

    @staticmethod
    def get_language_difficulty_name(language: "Language") -> str:
        """Получить локализованное название сложности языка.

        Args:
            language: Объект языка

        Returns:
            Локализованное название сложности языка.
        """
        diff_name = t(f"language.difficulties.{language.difficulty}")
        return _safe_str(diff_name)
