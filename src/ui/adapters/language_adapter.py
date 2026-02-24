"""Адаптер языка для UI слоя.

Преобразует доменные сущности языка в формат подходящий для UI,
изолируя UI от прямых зависимостей от доменной логики.
"""

from src.domain.entities.language import Language as DomainLanguage


class Language:
    """UI адаптер для языка."""

    def __init__(self, domain_language: DomainLanguage):
        """Инициализировать адаптер языка.

        Args:
            domain_language: Доменная сущность языка
        """
        self._language = domain_language

    @property
    def code(self) -> str:
        """Код языка."""
        return self._language.code

    @property
    def name(self) -> str:
        """Название языка."""
        return getattr(self._language, "name", self._language.code.title())

    def is_learnable_by_race(self, race_code: str) -> bool:
        """Проверить, доступен ли язык для расы."""
        if hasattr(self._language, "is_learnable_by_race"):
            result = self._language.is_learnable_by_race(race_code)
            return bool(result)
        return False

    def is_learnable_by_class(self, class_code: str) -> bool:
        """Проверить, доступен ли язык для класса."""
        if hasattr(self._language, "is_learnable_by_class"):
            result = self._language.is_learnable_by_class(class_code)
            return bool(result)
        return False

    def can_be_learned_by_character(
        self, race_code: str | None, class_code: str | None
    ) -> bool:
        """Проверить, может ли персонаж изучить язык."""
        if hasattr(self._language, "can_be_learned_by_character"):
            return self._language.can_be_learned_by_character(
                race_code or "", class_code or ""
            )
        return False

    def __str__(self) -> str:
        """Строковое представление."""
        return getattr(self._language, "name", self._language.code.title())


# Псевдоним для обратной совместимости
LanguageAdapter = Language
