"""Валидатор имени персонажа."""

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Результат валидации имени."""

    is_valid: bool
    error_message: str | None = None

    @classmethod
    def success(cls) -> "ValidationResult":
        """Успешная валидация."""
        return cls(is_valid=True)

    @classmethod
    def failure(cls, message: str) -> "ValidationResult":
        """Неуспешная валидация с сообщением об ошибке."""
        return cls(is_valid=False, error_message=message)


class NameValidator:
    """Валидатор имени персонажа.

    Применяемые паттерны:
    - Validator (Валидатор) — инкапсулирует логику проверки данных
    - Result Object (Объект-результат) — возвращает детальную информацию о результате

    Применяемые принципы:
    - Single Responsibility — только валидация имени
    - Explicit > Implicit — явные правила и сообщения об ошибках
    - Fail Fast — немедленное обнаружение ошибок
    """

    # Константы согласно требованиям из docs/character_creation/01_name_input.md
    MIN_LENGTH = 3
    MAX_LENGTH = 16
    ALLOWED_PATTERN = re.compile(r"^[a-zA-Zа-яА-ЯёЁ\-]+$")

    def validate(self, name: str) -> ValidationResult:
        """Валидировать имя персонажа.

        Args:
            name: Имя персонажа для валидации

        Returns:
            ValidationResult с детальной информацией о результате
        """
        # Проверка на пустую строку
        if not name or not name.strip():
            return ValidationResult.failure("Имя не может быть пустым")

        # Удаление лишних пробелов
        trimmed_name = name.strip()

        # Проверка длины
        if len(trimmed_name) < self.MIN_LENGTH:
            return ValidationResult.failure(
                f"Имя должно содержать минимум {self.MIN_LENGTH} символа "
                f"(текущая длина: {len(trimmed_name)})"
            )

        if len(trimmed_name) > self.MAX_LENGTH:
            return ValidationResult.failure(
                f"Имя должно содержать максимум {self.MAX_LENGTH} символов "
                f"(текущая длина: {len(trimmed_name)})"
            )

        # Проверка разрешенных символов
        if not self.ALLOWED_PATTERN.match(trimmed_name):
            return ValidationResult.failure(
                "Имя может содержать только буквы и дефисы. "
                "Цифры и спецсимволы запрещены."
            )

        # Проверка на дефисы в начале и конце
        if trimmed_name.startswith("-") or trimmed_name.endswith("-"):
            return ValidationResult.failure(
                "Имя не может начинаться или заканчиваться дефисом"
            )

        # Проверка на двойные дефисы
        if "--" in trimmed_name:
            return ValidationResult.failure(
                "Имя не может содержать двойные дефисы"
            )

        return ValidationResult.success()

    def is_valid(self, name: str) -> bool:
        """Быстрая проверка валидности (только True/False).

        Args:
            name: Имя персонажа для проверки

        Returns:
            True если имя валидно, иначе False
        """
        return self.validate(name).is_valid
