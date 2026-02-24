"""Доменная сущность Языка.

Чистая сущность D&D, содержащая только бизнес-логику языков.
Не зависит от внешних слоев согласно Clean Architecture.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional


@dataclass(frozen=True)
class LanguageMechanics:
    """Игровые механики языка.

    Value Object представляющий правила и ограничения языка.
    """

    script: str = ""
    is_default: bool = False
    learnable_by_all: bool = False
    learnable_by: list[str] = field(default_factory=list)
    race_bonus: list[str] = field(default_factory=list)
    learnable_by_special: list[str] = field(default_factory=list)
    magic_language: bool = False
    secret_language: bool = False
    evil_alignment: bool = False
    good_alignment: bool = False
    lawful_evil_alignment: bool = False


@dataclass(frozen=True)
class Language:
    """Язык в D&D.

    Доменная сущность содержащая бизнес-правила языков.
    Следует принципам Clean Architecture.
    """

    code: str
    type: str
    difficulty: str
    localization_keys: dict[str, str] = field(default_factory=dict)
    mechanics: LanguageMechanics = field(default_factory=LanguageMechanics)
    fallback_data: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        if not self.code.strip():
            raise ValueError("Код языка не может быть пустым")

        if not self.type.strip():
            raise ValueError("Тип языка не может быть пустым")

        if not self.difficulty.strip():
            raise ValueError("Сложность языка не может быть пустой")

        # Валидация формата кода
        if not self.code.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Код языка должен содержать только буквы, цифры, _ и -"
            )

    def is_available_for_race(self, race_code: str) -> bool:
        """Проверить доступность языка для расы.

        Args:
            race_code: Код расы для проверки

        Returns:
            True если язык доступен для расы
        """
        return (
            self.mechanics.learnable_by_all
            or race_code in self.mechanics.learnable_by
            or race_code in self.mechanics.race_bonus
        )

    def is_available_for_class(self, class_code: str) -> bool:
        """Проверить доступность языка для класса.

        Args:
            class_code: Код класса для проверки

        Returns:
            True если язык доступен для класса
        """
        return class_code in self.mechanics.learnable_by_special

    def is_magic_language(self) -> bool:
        """Проверить, является ли язык магическим.

        Returns:
            True если язык магический
        """
        return self.mechanics.magic_language

    def is_secret_language(self) -> bool:
        """Проверить, является ли язык секретным.

        Returns:
            True если язык секретный
        """
        return self.mechanics.secret_language

    def requires_special_alignment(self) -> str | None:
        """Проверить требование к мировоззрению.

        Returns:
            Требуемое мировоззрение или None если нет требований
        """
        if self.mechanics.evil_alignment:
            return "evil"
        elif self.mechanics.good_alignment:
            return "good"
        elif self.mechanics.lawful_evil_alignment:
            return "lawful_evil"
        return None

    def get_learning_difficulty_score(self) -> int:
        """Получить числовую оценку сложности изучения.

        Returns:
            Оценка сложности (1-5, где 1 - легко, 5 - очень сложно)
        """
        difficulty_scores = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
            "very_hard": 4,
            "extreme": 5,
        }
        return difficulty_scores.get(self.difficulty.lower(), 2)

    def can_be_learned_by_character(
        self, race_code: str, class_code: str | None = None
    ) -> bool:
        """Проверить, может ли персонаж изучить язык.

        Args:
            race_code: Код расы персонажа
            class_code: Опциональный код класса персонажа

        Returns:
            True если язык доступен для изучения
        """
        # Базовая проверка доступности для расы
        if not self.is_available_for_race(race_code):
            return False

        # Проверка требований к мировоззрению (если бы у нас была эта информация)
        # alignment_requirement = self.requires_special_alignment()
        # if alignment_requirement and character.alignment != alignment_requirement:
        #     return False

        # Проверка доступности для класса
        if class_code and not self.is_available_for_class(class_code):
            # Если язык доступен только для определённых классов
            if self.mechanics.learnable_by_special:
                return False

        return True

    def get_localized_name(
        self, localization_service: Optional["ILocalizationService"] = None
    ) -> str:
        """Получить локализованное название языка.

        Args:
            localization_service: Сервис локализации

        Returns:
            Локализованное название или fallback
        """
        if localization_service and "name" in self.localization_keys:
            try:
                result = localization_service.translate(
                    self.localization_keys["name"]
                )
                return (
                    result
                    if isinstance(result, str)
                    else self.fallback_data.get("name", self.code.title())
                )
            except Exception:
                pass  # Fallback если перевод не найден

        # Fallback данные
        return self.fallback_data.get("name", self.code.title())

    def get_localized_description(
        self, localization_service: Optional["ILocalizationService"] = None
    ) -> str:
        """Получить локализованное описание языка.

        Args:
            localization_service: Сервис локализации

        Returns:
            Локализованное описание или fallback
        """
        if localization_service and "description" in self.localization_keys:
            try:
                result = localization_service.translate(
                    self.localization_keys["description"]
                )
                return (
                    result
                    if isinstance(result, str)
                    else self.fallback_data.get(
                        "description", f"Язык: {self.code}"
                    )
                )
            except Exception:
                pass

        # Fallback описание
        return self.fallback_data.get("description", f"Язык: {self.code}")

    def is_exotic_language(self) -> bool:
        """Проверить, является ли язык экзотическим.

        Returns:
            True если язык экзотический
        """
        return self.type.lower() == "exotic"

    def is_standard_language(self) -> bool:
        """Проверить, является ли язык стандартным.

        Returns:
            True если язык стандартный
        """
        return self.type.lower() == "standard"

    def __str__(self) -> str:
        """Строковое представление."""
        return f"Language({self.code})"

    def __repr__(self) -> str:
        """Детальное строковое представление."""
        return (
            f"Language(code='{self.code}', type='{self.type}', "
            f"difficulty='{self.difficulty}', magic={self.mechanics.magic_language})"
        )


# Импорт для аннотации
if TYPE_CHECKING:
    from src.interfaces.services import ILocalizationService
