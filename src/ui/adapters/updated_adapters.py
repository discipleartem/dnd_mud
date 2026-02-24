"""Обновленные адаптеры для UI слоя с использованием DTO.

Этот файл заменяет старые адаптеры и использует новые DTO
следуя принципам Clean Architecture.
"""

from src.domain.entities.character import Character as DomainCharacter
from src.domain.entities.race import (
    Race as DomainRace,
)
from src.domain.value_objects.ability_scores import (
    AbilityScores as DomainAbilityScores,
)
from src.ui.adapters.domain_adapters import (
    AbilityScoresAdapter,
    RaceAdapter,
)
from src.ui.adapters.domain_adapters import (
    CharacterAdapter as BaseCharacterAdapter,
)
from src.ui.dto.character_dto import (
    AbilityScoreDTO,
    CharacterDTO,
    RaceDTO,
)


class Size:
    """Упрощенный класс Size для UI адаптеров."""

    def __init__(self, size_category: str = "medium"):
        self.category = size_category

    def get_localized_name(self) -> str:
        """Получить локализованное название размера."""
        size_names = {
            "tiny": "Крошечный",
            "small": "Маленький",
            "medium": "Средний",
            "large": "Большой",
            "huge": "Огромный",
            "gargantuan": "Гигантский",
        }
        return size_names.get(self.category, "Средний")


class Character:
    """UI адаптер для персонажа с использованием DTO.

    Этот класс теперь является оберткой над DTO для обратной совместимости.
    В будущем будет заменен прямым использованием DTO.
    """

    def __init__(self, character_dto: CharacterDTO | None = None):
        """Инициализировать адаптер.

        Args:
            character_dto: DTO персонажа
        """
        self._dto = character_dto or CharacterDTO(name="Безымянный")

    @property
    def name(self) -> str:
        """Имя персонажа."""
        return self._dto.name

    @property
    def race(self) -> RaceDTO | None:
        """Раса персонажа."""
        return None  # Будет реализовано через Use Cases

    @property
    def level(self) -> int:
        """Уровень персонажа."""
        return self._dto.level

    @property
    def ability_scores(self) -> AbilityScoreDTO | None:
        """Характеристики персонажа."""
        if not self._dto.ability_scores:
            return None
        return AbilityScoreDTO(
            strength=self._dto.ability_scores.get("strength", {}).get(
                "value", 10
            ),
            dexterity=self._dto.ability_scores.get("dexterity", {}).get(
                "value", 10
            ),
            constitution=self._dto.ability_scores.get("constitution", {}).get(
                "value", 10
            ),
            intelligence=self._dto.ability_scores.get("intelligence", {}).get(
                "value", 10
            ),
            wisdom=self._dto.ability_scores.get("wisdom", {}).get("value", 10),
            charisma=self._dto.ability_scores.get("charisma", {}).get(
                "value", 10
            ),
        )

    def set_ability_scores(self, ability_scores: "AbilityScoreDTO") -> None:
        """Установить характеристики персонажа.

        Args:
            ability_scores: Характеристики персонажа
        """
        self._dto.ability_scores = ability_scores.to_dict()
        self._dto.ability_modifiers = ability_scores.get_all_modifiers()

    def update_race(
        self, race: RaceDTO, subrace: RaceDTO | None = None
    ) -> None:
        """Обновить расу и подрасу персонажа.

        Args:
            race: Новая раса
            subrace: Новая подраса
        """
        self._dto.race_name = race.name
        if subrace:
            self._dto.subrace_name = subrace.name

    def get_dto(self) -> CharacterDTO:
        """Получить DTO персонажа.

        Returns:
            DTO персонажа
        """
        return self._dto

    @classmethod
    def from_domain(cls, character: DomainCharacter) -> "Character":
        """Создать адаптер из доменной сущности.

        Args:
            character: Доменная сущность персонажа

        Returns:
            Адаптер для UI
        """
        dto = BaseCharacterAdapter.to_dto(character)
        return cls(dto)


class Race:
    """UI адаптер для расы с использованием DTO."""

    def __init__(self, race_dto: RaceDTO | None = None):
        """Инициализировать адаптер.

        Args:
            race_dto: DTO расы
        """
        self._dto = race_dto or RaceDTO(name="Без расы")

    @property
    def name(self) -> str:
        """Название расы."""
        return self._dto.name

    @property
    def speed(self) -> int:
        """Скорость расы."""
        return self._dto.speed

    @property
    def ability_bonuses(self) -> dict[str, int]:
        """Бонусы характеристик расы."""
        return self._dto.ability_bonuses

    @property
    def languages(self) -> list[str]:
        """Языки расы."""
        return self._dto.languages

    @property
    def ability_bonuses_description(self) -> str:
        """Описание бонусов характеристик расы."""
        return getattr(self._dto, "ability_bonuses_description", "")

    @property
    def features(self) -> list[dict]:
        """Особенности расы."""
        return getattr(self._dto, "features", [])

    @property
    def size(self) -> "Size":
        """Размер расы."""
        return Size(getattr(self._dto, "size", "medium"))

    @property
    def allow_base_race_choice(self) -> bool:
        """Разрешить выбор базовой расы."""
        return getattr(self._dto, "allow_base_race_choice", False)

    def get_languages_display(self) -> str:
        """Получить отображение языков."""
        return ", ".join(self.languages) if self.languages else "Нет языков"

    @property
    def subraces(self) -> list["Race"]:
        """Подрасы."""
        return [Race(subrace_dto) for subrace_dto in self._dto.subraces]

    def get_dto(self) -> RaceDTO:
        """Получить DTO расы.

        Returns:
            DTO расы
        """
        return self._dto

    @classmethod
    def from_domain(cls, race: DomainRace) -> "Race":
        """Создать адаптер из доменной сущности.

        Args:
            race: Доменная сущность расы

        Returns:
            Адаптер для UI
        """
        dto = RaceAdapter.to_dto(race)
        return cls(dto)


class SubRace:
    """UI адаптер для подрасы с использованием DTO."""

    def __init__(self, subrace_dto: RaceDTO | None = None):
        """Инициализировать адаптер.

        Args:
            subrace_dto: DTO подрасы
        """
        self._dto = subrace_dto or RaceDTO(name="Без подрасы")

    @property
    def name(self) -> str:
        """Название подрасы."""
        return self._dto.name

    @property
    def ability_bonuses(self) -> dict[str, int]:
        """Бонусы характеристик подрасы."""
        return self._dto.ability_bonuses

    @property
    def languages(self) -> list[str]:
        """Языки подрасы."""
        return self._dto.languages

    @property
    def ability_bonuses_description(self) -> str:
        """Описание бонусов характеристик подрасы."""
        return getattr(self._dto, "ability_bonuses_description", "")

    @property
    def features(self) -> list[dict]:
        """Особенности подрасы."""
        return getattr(self._dto, "features", [])

    @property
    def speed(self) -> int:
        """Скорость подрасы."""
        return getattr(self._dto, "speed", 30)

    @property
    def size(self) -> "Size":
        """Размер подрасы."""
        return Size(getattr(self._dto, "size", "medium"))

    def get_dto(self) -> RaceDTO:
        """Получить DTO подрасы.

        Returns:
            DTO подрасы
        """
        return self._dto


class AbilityScores:
    """UI адаптер для характеристик с использованием DTO."""

    def __init__(self, ability_scores_dto: AbilityScoreDTO | None = None):
        """Инициализировать адаптер.

        Args:
            ability_scores_dto: DTO характеристик
        """
        self._dto = ability_scores_dto or AbilityScoreDTO()

    @property
    def strength(self) -> int:
        """Сила."""
        return self._dto.strength

    @property
    def dexterity(self) -> int:
        """Ловкость."""
        return self._dto.dexterity

    @property
    def constitution(self) -> int:
        """Телосложение."""
        return self._dto.constitution

    @property
    def intelligence(self) -> int:
        """Интеллект."""
        return self._dto.intelligence

    @property
    def wisdom(self) -> int:
        """Мудрость."""
        return self._dto.wisdom

    @property
    def charisma(self) -> int:
        """Харизма."""
        return self._dto.charisma

    def get_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики.

        Args:
            ability: Название характеристики

        Returns:
            Модификатор характеристики
        """
        return self._dto.get_modifier(ability)

    def get_all_modifiers(self) -> dict[str, int]:
        """Получить все модификаторы.

        Returns:
            Словарь модификаторов
        """
        return self._dto.get_all_modifiers()

    def get_dto(self) -> AbilityScoreDTO:
        """Получить DTO характеристик.

        Returns:
            DTO характеристик
        """
        return self._dto

    @classmethod
    def from_domain(
        cls, ability_scores: DomainAbilityScores
    ) -> "AbilityScores":
        """Создать адаптер из доменных характеристик.

        Args:
            ability_scores: Доменные характеристики

        Returns:
            Адаптер для UI
        """
        dto = AbilityScoresAdapter.to_dto(ability_scores)
        return cls(dto)


# Фабрики для создания адаптеров
class CharacterAdapterFactory:
    """Фабрика для создания адаптеров персонажей."""

    @staticmethod
    def create_from_domain(character: DomainCharacter) -> Character:
        """Создать адаптер персонажа из доменной сущности.

        Args:
            character: Доменная сущность персонажа

        Returns:
            Адаптер персонажа
        """
        return Character.from_domain(character)

    @staticmethod
    def create_from_dto(dto: CharacterDTO) -> Character:
        """Создать адаптер персонажа из DTO.

        Args:
            dto: DTO персонажа

        Returns:
            Адаптер персонажа
        """
        return Character(dto)


class RaceAdapterFactory:
    """Фабрика для создания адаптеров рас."""

    @staticmethod
    def create_from_domain(race: DomainRace) -> Race:
        """Создать адаптер расы из доменной сущности.

        Args:
            race: Доменная сущность расы

        Returns:
            Адаптер расы
        """
        return Race.from_domain(race)
