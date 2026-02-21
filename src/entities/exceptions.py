"""Исключения бизнес-логики.

Определяет специфические исключения для предметной области.
"""


class DnDError(Exception):
    """Базовое исключение D&D."""
    pass


class InvalidCharacterDataError(DnDError):
    """Ошибка валидации данных персонажа."""
    pass


class CharacterNotFoundError(DnDError):
    """Персонаж не найден."""
    pass


class InvalidAbilityError(DnDError):
    """Ошибка валидации характеристики."""
    pass


class RaceNotFoundError(DnDError):
    """Раса не найдена."""
    pass


class ClassNotFoundError(DnDError):
    """Класс не найден."""
    pass