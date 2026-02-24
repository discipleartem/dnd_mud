"""Доменная сущность Расы.

Чистая сущность D&D, содержащая только бизнес-логику и правила.
Не зависит от внешних слоев согласно Clean Architecture.
"""

from dataclasses import dataclass, field
from typing import Any

from src.domain.value_objects.size import Size, SizeCategory


@dataclass(frozen=True)
class Feature:
    """Черта расы или подрасы.

    Value Object представляющий особенность или способность.
    """

    name: str
    description: str
    mechanics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SubRace:
    """Подраса.

    Value Object представляющий вариант основной расы.
    """

    name: str
    description: str
    ability_bonuses: dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    languages: list[str] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    inherit_base_abilities: bool = True


@dataclass(frozen=True)
class Race:
    """Раса персонажа D&D.

    Доменная сущность содержащая бизнес-правила и логику рас.
    Следует принципам Clean Architecture - не зависит от внешних слоев.
    """

    name: str
    description: str
    ability_bonuses: dict[str, int] = field(default_factory=dict)
    ability_bonuses_description: str = ""
    size: Size = Size.from_category(SizeCategory.MEDIUM)
    speed: int = 30
    age: dict[str, int] = field(default_factory=dict)
    languages: list[str] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    subraces: dict[str, SubRace] = field(default_factory=dict)
    allow_base_race_choice: bool = False

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        if not self.name.strip():
            raise ValueError("Название расы не может быть пустым")

        if not self.description.strip():
            raise ValueError("Описание расы не может быть пустым")

        if self.speed <= 0:
            raise ValueError("Скорость должна быть положительным числом")

        # Валидация бонусов характеристик
        for ability, bonus in self.ability_bonuses.items():
            if not isinstance(bonus, int) or bonus < 0:
                raise ValueError(
                    f"Бонус к {ability} должен быть положительным числом"
                )

    def get_effective_ability_bonuses(
        self, subrace: SubRace | None = None
    ) -> dict[str, int]:
        """Получить итоговые бонусы к характеристикам.

        Args:
            subrace: Опциональная подраса

        Returns:
            Словарь итоговых бонусов к характеристикам
        """
        final_bonuses = {}

        # Добавляем бонусы базовой расы если нужно
        if self._should_include_base_abilities(subrace):
            final_bonuses.update(self.ability_bonuses)

        # Добавляем бонусы подрасы
        if subrace is not None:
            final_bonuses.update(subrace.ability_bonuses)

        return final_bonuses

    def _should_include_base_abilities(self, subrace: SubRace | None) -> bool:
        """Проверить, нужно ли включать бонусы базовой расы.

        Args:
            subrace: Опциональная подраса

        Returns:
            True если нужно включить бонусы базовой расы
        """
        return subrace is None or subrace.inherit_base_abilities

    def get_all_languages(self, subrace: SubRace | None = None) -> list[str]:
        """Получить все доступные языки.

        Args:
            subrace: Опциональная подраса

        Returns:
            Список уникальных языков
        """
        languages = set(self.languages)

        if subrace:
            languages.update(subrace.languages)

        return sorted(languages)

    def get_all_features(
        self, subrace: SubRace | None = None
    ) -> list[Feature]:
        """Получить все черты расы и подрасы.

        Args:
            subrace: Опциональная подраса

        Returns:
            Список всех черт
        """
        features = list(self.features)

        if subrace:
            features.extend(subrace.features)

        return features

    def has_subrace(self, subrace_name: str) -> bool:
        """Проверить наличие подрасы.

        Args:
            subrace_name: Название подрасы

        Returns:
            True если подраса существует
        """
        return any(
            subrace.name.lower() == subrace_name.lower()
            for subrace in self.subraces.values()
        )

    def get_subrace_by_name(self, subrace_name: str) -> SubRace | None:
        """Получить подрасу по названию.

        Args:
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        for subrace in self.subraces.values():
            if subrace.name.lower() == subrace_name.lower():
                return subrace
        return None

    def can_choose_subrace(self) -> bool:
        """Проверить, можно ли выбирать подрасу.

        Returns:
            True если есть подрасы или разрешён выбор базовой расы
        """
        return bool(self.subraces) or self.allow_base_race_choice

    def get_age_category(self, age: int) -> str:
        """Получить возрастную категорию.

        Args:
            age: Возраст персонажа

        Returns:
            Возрастная категория
        """
        if not self.age:
            return "unknown"

        adult_age = self.age.get("adult", 18)
        max_age = self.age.get("max", 100)

        if age < adult_age:
            return "young"
        elif age < max_age * 0.5:
            return "adult"
        elif age < max_age * 0.8:
            return "middle_aged"
        elif age < max_age:
            return "old"
        else:
            return "venerable"

    def validate_character_compatibility(
        self, character_data: dict[str, Any]
    ) -> list[str]:
        """Валидировать совместимость расы с данными персонажа.

        Args:
            character_data: Данные персонажа для валидации

        Returns:
            Список ошибок валидации
        """
        errors = []

        # Проверка скорости (базовая валидация)
        if "speed" in character_data:
            character_speed = character_data["speed"]
            if (
                character_speed > self.speed * 2
            ):  # Не более чем в 2 раза больше базовой
                errors.append(
                    f"Скорость {character_speed} слишком высокая для расы {self.name}"
                )

        # Проверка размера
        if "size" in character_data:
            character_size = character_data["size"]
            if (
                isinstance(character_size, str)
                and character_size != self.size.category.value
            ):
                # Некоторые расы могут иметь разные размеры, но это требует специальной логики
                pass  # Пока пропускаем эту проверку

        return errors

    def __str__(self) -> str:
        """Строковое представление."""
        return f"Race({self.name})"

    def __repr__(self) -> str:
        """Детальное строковое представление."""
        return (
            f"Race(name='{self.name}', size={self.size.category.value}, "
            f"speed={self.speed}, languages={len(self.languages)}, "
            f"subraces={len(self.subraces)})"
        )
