"""Value Object для языка.

Следует KISS и YAGNI - просто и без излишеств.
"""

from ..constants import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


class Language:
    """Неизменяемый объект языка.

    Следует KISS и YAGNI - просто и понятно.
    """

    def __init__(self, code: str) -> None:
        """Инициализация языка."""
        self._code = code.strip().lower()
        self._validate_code()

    def _validate_code(self) -> None:
        """Валидировать код языка."""
        if not isinstance(self._code, str):
            raise ValueError("Код языка должен быть строкой")

        if not self._code:
            raise ValueError("Код языка не может быть пустым")

        if len(self._code) != 2:
            raise ValueError("Код языка должен состоять из 2 символов")

        if self._code not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Язык '{self._code}' не поддерживается. "
                f"Поддерживаемые: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )

    def get_code(self) -> str:
        """Получить код языка."""
        return self._code

    @classmethod
    def from_string(cls, language_code: str) -> "Language":
        """Создать из строки."""
        return cls(language_code)

    @classmethod
    def create_default(cls) -> "Language":
        """Создать язык по умолчанию."""
        return cls(DEFAULT_LANGUAGE)

    def __str__(self) -> str:
        """Строковое представление."""
        return self._code

    def __eq__(self, other) -> bool:
        """Сравнение объектов по значению."""
        if not isinstance(other, Language):
            return False
        return self._code == other._code

    def __hash__(self) -> int:
        """Хеш объекта на основе значения."""
        return hash(self._code)
