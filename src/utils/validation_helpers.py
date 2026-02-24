"""Утилиты для валидации данных.

Содержит общие функции валидации, используемые во всем проекте.
Следует DRY принципу - Don't Repeat Yourself.
"""

from typing import Any


def validate_non_empty_string(value: str, field_name: str) -> None:
    """Валидировать что строка не пустая.

    Args:
        value: Значение для проверки
        field_name: Название поля для ошибки

    Raises:
        ValueError: Если строка пустая
    """
    if not value.strip():
        raise ValueError(f"{field_name} не может быть пустым")


def validate_range(
    value: int, min_value: int, max_value: int, field_name: str
) -> None:
    """Валидировать что значение входит в диапазон.

    Args:
        value: Значение для проверки
        min_value: Минимальное значение
        max_value: Максимальное значение
        field_name: Название поля для ошибки

    Raises:
        ValueError: Если значение вне диапазона
    """
    if value < min_value or value > max_value:
        raise ValueError(
            f"{field_name} должно быть в диапазоне {min_value}-{max_value}"
        )


def validate_positive_integer(value: Any, field_name: str) -> int:
    """Валидировать что значение является положительным целым числом.

    Args:
        value: Значение для проверки
        field_name: Название поля для ошибки

    Returns:
        Проверенное целое число

    Raises:
        ValueError: Если значение не является положительным целым числом
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError(
            f"{field_name} должно быть положительным целым числом"
        )

    return value


def validate_required_fields(
    data: dict, required_fields: list[str]
) -> list[str]:
    """Проверить наличие обязательных полей в данных.

    Args:
        data: Словарь с данными
        required_fields: Список обязательных полей

    Returns:
        Список отсутствующих полей
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    return missing_fields
