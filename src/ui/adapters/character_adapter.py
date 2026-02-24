"""Адаптер персонажа для UI слоя.

Преобразует доменные сущности в формат подходящий для UI,
изолируя UI от прямых зависимостей от доменной логики.
Следует принципам Clean Architecture и Adapter Pattern.
"""

from typing import TYPE_CHECKING, Any, Optional

from i18n import t
from src.domain.entities.character import Character as DomainCharacter
from src.domain.entities.race import Race as DomainRace
from src.domain.entities.race import SubRace as DomainSubRace
from src.domain.value_objects.ability_scores import (
    AbilityScores as DomainAbilityScores,
)
from src.domain.value_objects.size import Size as DomainSize

if TYPE_CHECKING:
    from .language_adapter import Language


class Size:
    """UI адаптер для размера персонажа с локализацией."""

    def __init__(self, domain_size: DomainSize):
        """Инициализировать адаптер размера.

        Args:
            domain_size: Доменный объект размера
        """
        self._domain_size = domain_size

    def get_localized_name(self) -> str:
        """Получить локализованное название размера."""
        result = t(f"character.size.{self._domain_size.category.value}")
        return result if isinstance(result, str) else str(result)

    def __str__(self) -> str:
        """Строковое представление с локализацией."""
        return self.get_localized_name()


class Character:
    """UI адаптер для персонажа.

    Предоставляет удобный интерфейс для UI слоя,
    скрывая сложность доменной логики.
    """

    def __init__(self, domain_character: DomainCharacter):
        """Инициализировать адаптер персонажа.

        Args:
            domain_character: Доменная сущность персонажа
        """
        self._character = domain_character

    @property
    def name(self) -> str:
        """Имя персонажа."""
        return self._character.name

    @property
    def race(self) -> Optional["Race"]:
        """Раса персонажа."""
        if self._character.race:
            return Race(self._character.race)
        return None

    @race.setter
    def race(self, value: Optional["Race"]) -> None:
        """Установить расу персонажа.

        Args:
            value: UI адаптер расы или None
        """
        if value is None:
            self._character.race = None
        else:
            self._character.race = value._race

    @property
    def character_class(self) -> str:
        """Класс персонажа."""
        return self._character.character_class

    @property
    def level(self) -> int:
        """Уровень персонажа."""
        return self._character.level

    @property
    def subrace(self) -> Optional["SubRace"]:
        """Подраса персонажа."""
        if self._character.subrace:
            return SubRace(self._character.subrace)
        return None

    @property
    def sub_class(self) -> str | None:
        """Подкласс персонажа."""
        return self._character.sub_class

    @property
    def ability_scores(self) -> Optional["AbilityScores"]:
        """Характеристики персонажа."""
        if self._character.ability_scores:
            return AbilityScores(self._character.ability_scores)
        return None

    @property
    def size(self) -> Size:
        """Размер персонажа с локализацией."""
        return Size(self._character.size)

    @property
    def speed(self) -> int:
        """Скорость персонажа."""
        return self._character.speed

    @property
    def languages(self) -> list[str]:
        """Языки персонажа."""
        return self._character.languages

    def get_language_objects(self) -> list["Language"]:
        """Получить объекты языков персонажа.

        Returns:
            Список объектов языков с поддержкой локализации
        """
        if TYPE_CHECKING:
            from .language_adapter import Language
        else:
            from .language_adapter import Language

        domain_languages = self._character.get_learnable_languages([])
        return [Language(lang) for lang in domain_languages]

    def get_learnable_languages(self) -> list["Language"]:
        """Получить языки, которые может изучить персонаж."""
        if TYPE_CHECKING:
            from .language_adapter import Language
        else:
            from .language_adapter import Language

        domain_languages = self._character.get_learnable_languages([])
        return [Language(lang) for lang in domain_languages]

    def can_learn_language(self, lang_code: str) -> bool:
        """Проверить, может ли персонаж изучить конкретный язык."""

        # Заглушка - будет реализовано при рефакторинге языков
        return lang_code not in self.languages

    def _normalize_entity_name(self, entity_name: str) -> str:
        """Нормализовать имя сущности для поиска."""
        return entity_name.lower().replace(" ", "_")

    def update_race(
        self, race: Optional["Race"], subrace: Optional["SubRace"]
    ) -> None:
        """Обновить расу и подрасу персонажа.

        Args:
            race: UI адаптер расы или None
            subrace: UI адаптер подрасы или None
        """
        self._character.race = race._race if race else None
        self._character.subrace = subrace._subrace if subrace else None

    def set_ability_scores(self, ability_scores: "AbilityScores") -> None:
        """Установить характеристики персонажа.

        Args:
            ability_scores: UI адаптер характеристик
        """
        self._character.ability_scores = ability_scores._ability_scores

    def __str__(self) -> str:
        """Строковое представление."""
        return str(self._character)


class Race:
    """UI адаптер для расы."""

    def __init__(self, domain_race: DomainRace):
        """Инициализировать адаптер расы.

        Args:
            domain_race: Доменная сущность расы
        """
        self._race = domain_race

    @property
    def name(self) -> str:
        """Название расы."""
        return self._race.name

    @property
    def size(self) -> Size:
        """Размер расы."""
        return Size(self._race.size)

    @property
    def speed(self) -> int:
        """Скорость расы."""
        return self._race.speed

    @property
    def ability_bonuses_description(self) -> str:
        """Описание бонусов характеристик."""
        return getattr(self._race, "ability_bonuses_description", "")

    @property
    def features(self) -> list:
        """Особенности расы."""
        return getattr(self._race, "features", [])

    @property
    def subraces(self) -> dict:
        """Подрасы."""
        return getattr(self._race, "subraces", {})

    @property
    def allow_base_race_choice(self) -> bool:
        """Разрешен ли выбор базовой расы."""
        return getattr(self._race, "allow_base_race_choice", True)

    def get_subrace_by_name(self, name: str) -> Optional["SubRace"]:
        """Получить подрасу по названию."""
        if hasattr(self._race, "get_subrace_by_name"):
            domain_subrace = self._race.get_subrace_by_name(name)
            if domain_subrace:
                return SubRace(domain_subrace)
        return None

    def get_languages_display(self) -> str:
        """Получить отображение языков."""
        if hasattr(self._race, "get_languages_display"):
            result = self._race.get_languages_display()
            return str(result)
        return ", ".join(self.languages)

    @property
    def languages(self) -> list[str]:
        """Языки расы."""
        return getattr(self._race, "languages", [])

    def __str__(self) -> str:
        """Строковое представление."""
        return self._race.name


class SubRace:
    """UI адаптер для подрасы."""

    def __init__(self, domain_subrace: DomainSubRace):
        """Инициализировать адаптер подрасы.

        Args:
            domain_subrace: Доменная сущность подрасы
        """
        self._subrace = domain_subrace

    @property
    def name(self) -> str:
        """Название подрасы."""
        return self._subrace.name

    @property
    def description(self) -> str:
        """Описание подрасы."""
        return getattr(self._subrace, "description", "")

    @property
    def ability_bonuses_description(self) -> str:
        """Описание бонусов характеристик."""
        return getattr(self._subrace, "ability_bonuses_description", "")

    @property
    def features(self) -> list:
        """Особенности подрасы."""
        return getattr(self._subrace, "features", [])

    def __str__(self) -> str:
        """Строковое представление."""
        return self._subrace.name


class AbilityScores:
    """UI адаптер для характеристик."""

    def __init__(self, domain_ability_scores: DomainAbilityScores):
        """Инициализировать адаптер характеристик.

        Args:
            domain_ability_scores: Доменные характеристики
        """
        self._ability_scores = domain_ability_scores

    def __getattr__(self, name: str) -> Any:
        """Проксировать вызовы к доменным характеристикам."""
        return getattr(self._ability_scores, name)

    def to_dict(self) -> dict:
        """Преобразовать в словарь."""
        if hasattr(self._ability_scores, "to_dict"):
            return self._ability_scores.to_dict()
        return {}


# Создадим псевдонимы для обратной совместимости
CharacterAdapter = Character
RaceAdapter = Race
SubRaceAdapter = SubRace
SizeAdapter = Size
AbilityScoresAdapter = AbilityScores
