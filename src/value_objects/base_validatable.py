"""Базовый класс для валидации.

Следует KISS и DRY - один метод для всех строковых полей.
"""

from typing import Final

from ..constants import (
    MAX_ASCII_ART_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_SUBTITLE_LENGTH,
    MAX_TITLE_LENGTH,
)

# Типы валидации для читаемости (Zen Python: явное лучше неявного)
TITLE_VALIDATION: Final[dict] = {"max_length": MAX_TITLE_LENGTH, "name": "Заголовок"}
SUBTITLE_VALIDATION: Final[dict] = {"max_length": MAX_SUBTITLE_LENGTH, "name": "Подзаголовок"}
DESCRIPTION_VALIDATION: Final[dict] = {"max_length": MAX_DESCRIPTION_LENGTH, "name": "Описание"}
ASCII_ART_VALIDATION: Final[dict] = {"max_length": MAX_ASCII_ART_LENGTH, "name": "ASCII-арт"}


class BaseValidatable:
    """Базовый класс для валидации.

    Следует KISS и DRY - один универсальный метод.
    """

    @staticmethod
    def validate_string(value: str, validation_config: dict, required: bool = True) -> str:
        """Универсальная валидация строковых полей.

        Args:
            value: Значение для валидации
            validation_config: Конфиг с max_length и name
            required: Обязательное поле

        Returns:
            Валидированная строка
        """
        if not isinstance(value, str):
            raise ValueError(f"{validation_config['name']} должен быть строкой")

        stripped_value = value.strip()

        if required and not stripped_value:
            raise ValueError(f"{validation_config['name']} не может быть пустым")

        max_length = validation_config.get("max_length")
        if max_length and len(stripped_value) > max_length:
            raise ValueError(
                f"{validation_config['name']} слишком длинный (максимум {max_length} символов)"
            )

        return stripped_value

    @staticmethod
    def validate_title(value: str) -> str:
        """Валидировать заголовок."""
        return BaseValidatable.validate_string(value, TITLE_VALIDATION)

    @staticmethod
    def validate_subtitle(value: str) -> str:
        """Валидировать подзаголовок."""
        return BaseValidatable.validate_string(value, SUBTITLE_VALIDATION)

    @staticmethod
    def validate_description(value: str) -> str:
        """Валидировать описание."""
        return BaseValidatable.validate_string(value, DESCRIPTION_VALIDATION)

    @staticmethod
    def validate_ascii_art(value: str) -> str:
        """Валидировать ASCII-арт."""
        return BaseValidatable.validate_string(value, ASCII_ART_VALIDATION, required=False)
