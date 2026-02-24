"""Доменная сущность Персонажа.

Чистая сущность D&D, содержащая только бизнес-логику персонажей.
Не зависит от внешних слоев согласно Clean Architecture.
"""

from dataclasses import dataclass, field
from typing import Any

from src.domain.entities.language import Language
from src.domain.entities.race import Race, SubRace
from src.domain.value_objects.ability_scores import AbilityScores
from src.domain.value_objects.size import Size, SizeCategory


@dataclass
class Character:
    """Персонаж D&D.

    Доменная сущность содержащая бизнес-правила персонажей.
    Следует принципам Clean Architecture - не зависит от внешних слоев.
    """

    name: str
    race: Race | None = None
    character_class: str = ""
    level: int = 1
    subrace: SubRace | None = None
    sub_class: str | None = None
    ability_scores: AbilityScores | None = None

    # Приватные поля для вычисляемых значений
    _known_languages: set[str] = field(
        default_factory=set, init=False, repr=False
    )
    _custom_languages: set[str] = field(
        default_factory=set, init=False, repr=False
    )

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        self._validate_name()
        self._validate_level()
        self._apply_race_bonuses()
        self._add_race_languages()

    def _validate_name(self) -> None:
        """Валидировать имя персонажа."""
        if not self.name or not self.name.strip():
            raise ValueError("Имя персонажа не может быть пустым")

        if len(self.name.strip()) < 2:
            raise ValueError(
                "Имя персонажа должно содержать минимум 2 символа"
            )

        if len(self.name.strip()) > 50:
            raise ValueError("Имя персонажа не может превышать 50 символов")

    def _validate_level(self) -> None:
        """Валидировать уровень персонажа."""
        if not isinstance(self.level, int):
            raise ValueError("Уровень должен быть целым числом")

        if self.level < 1 or self.level > 20:
            raise ValueError("Уровень персонажа должен быть в диапазоне 1-20")

    def _apply_race_bonuses(self) -> None:
        """Применить бонусы от расы к характеристикам."""
        if self.race and self.ability_scores:
            bonuses = self.race.get_effective_ability_bonuses(self.subrace)
            self.ability_scores = self.ability_scores.apply_bonuses(bonuses)

    def _add_race_languages(self) -> None:
        """Добавить языки от расы."""
        if self.race:
            race_languages = self.race.get_all_languages(self.subrace)
            self._known_languages.update(race_languages)

    @property
    def size(self) -> Size:
        """Получить размер персонажа от расы.

        Returns:
            Размер персонажа
        """
        return (
            self.race.size
            if self.race
            else Size.from_category(SizeCategory.MEDIUM)
        )

    @property
    def speed(self) -> int:
        """Получить скорость персонажа от расы.

        Returns:
            Скорость персонажа
        """
        return self.race.speed if self.race else 30

    @property
    def languages(self) -> list[str]:
        """Получить все известные языки персонажа.

        Returns:
            Список языков персонажа
        """
        all_languages = set(self._known_languages)
        all_languages.update(self._custom_languages)
        return sorted(all_languages)

    def get_age_category(self) -> str:
        """Получить возрастную категорию персонажа.

        Returns:
            Возрастная категория
        """
        if not self.race:
            return "unknown"

        # Предполагаем adulthood для простоты
        # В реальной игре здесь была бы логика с возрастом персонажа
        return "adult"

    def learn_language(self, language_code: str) -> bool:
        """Изучить новый язык.

        Args:
            language_code: Код языка для изучения

        Returns:
            True если язык успешно изучен

        Raises:
            ValueError: Если язык уже известен
        """
        if (
            language_code in self._known_languages
            or language_code in self._custom_languages
        ):
            raise ValueError(f"Персонаж уже знает язык: {language_code}")

        self._custom_languages.add(language_code)
        return True

    def forget_language(self, language_code: str) -> bool:
        """Забыть язык.

        Args:
            language_code: Код языка для забывания

        Returns:
            True если язык успешно забыт
        """
        removed = False

        if language_code in self._custom_languages:
            self._custom_languages.remove(language_code)
            removed = True

        return removed

    def knows_language(self, language_code: str) -> bool:
        """Проверить, знает ли персонаж язык.

        Args:
            language_code: Код языка для проверки

        Returns:
            True если язык известен
        """
        return (
            language_code in self._known_languages
            or language_code in self._custom_languages
        )

    def can_learn_language(self, language: Language) -> bool:
        """Проверить, может ли персонаж изучить язык.

        Args:
            language: Язык для проверки

        Returns:
            True если язык доступен для изучения
        """
        if not self.race:
            return False

        # Уже знает язык
        if self.knows_language(language.code):
            return False

        # Проверка доступности для расы
        race_code = self.race.name.lower().replace(" ", "_")
        return language.can_be_learned_by_character(
            race_code,
            self.character_class.lower() if self.character_class else None,
        )

    def get_learnable_languages(
        self, available_languages: list[Language]
    ) -> list[Language]:
        """Получить языки, которые может изучить персонаж.

        Args:
            available_languages: Список доступных языков

        Returns:
            Список языков доступных для изучения
        """
        learnable = []

        for language in available_languages:
            if self.can_learn_language(language):
                learnable.append(language)

        return learnable

    def get_ability_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики.

        Args:
            ability: Название характеристики

        Returns:
            Модификатор характеристики или 0 если нет характеристик
        """
        if not self.ability_scores:
            return 0

        return self.ability_scores.get_modifier(ability)

    def get_all_ability_modifiers(self) -> dict[str, int]:
        """Получить все модификаторы характеристик.

        Returns:
            Словарь модификаторов
        """
        if not self.ability_scores:
            return {}

        return self.ability_scores.get_all_modifiers()

    def change_race(
        self, new_race: Race, new_subrace: SubRace | None = None
    ) -> None:
        """Изменить расу персонажа.

        Args:
            new_race: Новая раса
            new_subrace: Новая подраса (опционально)
        """
        self.race = new_race
        self.subrace = new_subrace

        # Обновляем известные языки
        self._known_languages.clear()
        if new_race:
            race_languages = new_race.get_all_languages(new_subrace)
            self._known_languages.update(race_languages)

        # Пересчитываем характеристики с бонусами
        if self.ability_scores:
            bonuses = new_race.get_effective_ability_bonuses(new_subrace)
            self.ability_scores = self.ability_scores.apply_bonuses(bonuses)

    def level_up(self) -> None:
        """Повысить уровень персонажа.

        Raises:
            ValueError: Если персонаж уже на максимальном уровне
        """
        if self.level >= 20:
            raise ValueError("Персонаж уже на максимальном уровне")

        self.level += 1

    def validate(self) -> list[str]:
        """Валидировать персонажа.

        Returns:
            Список ошибок валидации
        """
        errors = []

        if not self.name.strip():
            errors.append("Имя персонажа не может быть пустым")

        if self.level < 1 or self.level > 20:
            errors.append("Уровень должен быть в диапазоне 1-20")

        if self.race and self.ability_scores:
            # Проверяем соответствие характеристик бонусам расы
            # Это сложная проверка, пока пропускаем
            pass

        return errors

    def get_summary(self) -> dict[str, Any]:
        """Получить сводную информацию о персонаже.

        Returns:
            Словарь с основной информацией
        """
        return {
            "name": self.name,
            "race": self.race.name if self.race else None,
            "subrace": self.subrace.name if self.subrace else None,
            "character_class": self.character_class,
            "sub_class": self.sub_class,
            "level": self.level,
            "size": self.size.category.value,
            "speed": self.speed,
            "languages": self.languages,
            "ability_scores": (
                self.ability_scores.to_dict() if self.ability_scores else None
            ),
            "ability_modifiers": self.get_all_ability_modifiers(),
        }

    def __str__(self) -> str:
        """Строковое представление."""
        race_name = self.race.name if self.race else "Без расы"
        class_info = f" {self.character_class}" if self.character_class else ""
        return f"{self.name} - {race_name}{class_info} {self.level} уровня"

    def __repr__(self) -> str:
        """Детальное строковое представление."""
        return (
            f"Character(name='{self.name}', race={self.race}, "
            f"class='{self.character_class}', level={self.level})"
        )
