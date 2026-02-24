"""DTO для UI слоя D&D MUD.

Data Transfer Objects для преобразования доменных сущностей
в формат удобный для отображения в пользовательском интерфейсе.
Следует принципам Clean Architecture - изолирует UI от домена.
"""

from dataclasses import dataclass
from typing import Any

from i18n import t


@dataclass
class CharacterDTO:
    """DTO для отображения персонажа в UI."""

    name: str
    race_name: str = "Без расы"
    subrace_name: str = ""
    character_class: str = ""
    sub_class: str = ""
    level: int = 1
    size_name: str = "Средний"
    speed: int = 30
    languages: list[str] = None  # type: ignore
    ability_scores: dict[str, dict[str, Any]] = None  # type: ignore
    ability_modifiers: dict[str, int] = None  # type: ignore

    def __post_init__(self) -> None:
        """Инициализация полей по умолчанию."""
        if self.languages is None:
            self.languages = []
        if self.ability_scores is None:
            self.ability_scores = {}
        if self.ability_modifiers is None:
            self.ability_modifiers = {}

    @classmethod
    def from_domain(cls, character: Any) -> "CharacterDTO":
        """Создать DTO из доменной сущности.

        Args:
            character: Доменная сущность персонажа

        Returns:
            DTO для отображения в UI
        """
        # Получаем сводную информацию от персонажа
        summary = character.get_summary()

        return cls(
            name=character.name,
            race_name=summary.get("race", "Без расы"),
            subrace_name=summary.get("subrace", ""),
            character_class=character.character_class,
            sub_class=character.sub_class or "",
            level=character.level,
            size_name=t(f"character.size.{summary.get('size', 'medium')}"),
            speed=summary.get("speed", 30),
            languages=summary.get("languages", []),
            ability_scores=summary.get("ability_scores", {}),
            ability_modifiers=summary.get("ability_modifiers", {}),
        )

    def get_display_name(self) -> str:
        """Получить отображаемое имя персонажа."""
        class_info = f" {self.character_class}" if self.character_class else ""
        return (
            f"{self.name} - {self.race_name}{class_info} {self.level} уровня"
        )

    def get_ability_score(self, ability: str) -> dict[str, Any]:
        """Получить информацию о характеристике."""
        return self.ability_scores.get(ability, {"value": 10, "modifier": 0})

    def get_ability_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики."""
        return self.ability_modifiers.get(ability, 0)


@dataclass
class RaceDTO:
    """DTO для отображения расы в UI."""

    name: str
    description: str = ""
    size_name: str = "Средний"
    speed: int = 30
    ability_bonuses: dict[str, int] = None  # type: ignore
    languages: list[str] = None  # type: ignore
    features: list[dict[str, Any]] = None  # type: ignore
    subraces: list["RaceDTO"] = None  # type: ignore

    def __post_init__(self) -> None:
        """Инициализация полей по умолчанию."""
        if self.ability_bonuses is None:
            self.ability_bonuses = {}
        if self.languages is None:
            self.languages = []
        if self.features is None:
            self.features = []
        if self.subraces is None:
            self.subraces = []

    @classmethod
    def from_domain(cls, race: Any) -> "RaceDTO":
        """Создать DTO из доменной сущности расы.

        Args:
            race: Доменная сущность расы

        Returns:
            DTO для отображения в UI
        """
        # Преобразуем черты в словари
        features = []
        if hasattr(race, "features") and race.features:
            for feature in race.features:
                features.append(
                    {
                        "name": feature.name,
                        "description": feature.description,
                        "mechanics": getattr(feature, "mechanics", {}),
                    }
                )

        # Преобразуем подрасы
        subraces = []
        if hasattr(race, "subraces") and race.subraces:
            for subrace in race.subraces:
                subraces.append(cls.from_domain(subrace))

        return cls(
            name=race.name,
            description=getattr(race, "description", ""),
            size_name=t(f"character.size.{race.size.category.value}"),
            speed=race.speed,
            ability_bonuses=getattr(race, "ability_bonuses", {}),
            languages=getattr(race, "languages", []),
            features=features,
            subraces=subraces,
        )

    def get_ability_bonus_display(self, ability: str) -> str:
        """Получить отображение бонуса характеристики."""
        bonus = self.ability_bonuses.get(ability, 0)
        return f"+{bonus}" if bonus > 0 else str(bonus)

    def has_subraces(self) -> bool:
        """Проверить наличие подрас."""
        return len(self.subraces) > 0


@dataclass
class LanguageDTO:
    """DTO для отображения языка в UI."""

    code: str
    name: str = ""
    description: str = ""
    type: str = "standard"
    is_learnable: bool = True

    @classmethod
    def from_domain(cls, language) -> "LanguageDTO":
        """Создать DTO из доменной сущности языка.

        Args:
            language: Доменная сущность языка

        Returns:
            DTO для отображения в UI
        """
        return cls(
            code=language.code,
            name=language.name,
            description=getattr(language, "description", ""),
            type=getattr(language, "type", "standard"),
            is_learnable=getattr(language, "is_learnable", True),
        )

    def get_display_name(self) -> str:
        """Получить отображаемое название языка."""
        return self.name if self.name else self.code.title()


@dataclass
class AbilityScoreDTO:
    """DTO для отображения характеристик персонажа."""

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def get_modifier(self, ability: str) -> int:
        """Получить модификатор характеристики."""
        value = getattr(self, ability.lower(), 10)
        return (value - 10) // 2

    def get_all_modifiers(self) -> dict[str, int]:
        """Получить все модификаторы."""
        return {
            "strength": self.get_modifier("strength"),
            "dexterity": self.get_modifier("dexterity"),
            "constitution": self.get_modifier("constitution"),
            "intelligence": self.get_modifier("intelligence"),
            "wisdom": self.get_modifier("wisdom"),
            "charisma": self.get_modifier("charisma"),
        }

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь для отображения."""
        return {
            "strength": {
                "value": self.strength,
                "modifier": self.get_modifier("strength"),
            },
            "dexterity": {
                "value": self.dexterity,
                "modifier": self.get_modifier("dexterity"),
            },
            "constitution": {
                "value": self.constitution,
                "modifier": self.get_modifier("constitution"),
            },
            "intelligence": {
                "value": self.intelligence,
                "modifier": self.get_modifier("intelligence"),
            },
            "wisdom": {
                "value": self.wisdom,
                "modifier": self.get_modifier("wisdom"),
            },
            "charisma": {
                "value": self.charisma,
                "modifier": self.get_modifier("charisma"),
            },
        }


@dataclass
class ValidationErrorDTO:
    """DTO для отображения ошибок валидации."""

    field: str
    message: str
    error_type: str = "error"

    def get_localized_message(self) -> str:
        """Получить локализованное сообщение."""
        return t(
            f"validation.{self.field}.{self.error_type}", default=self.message
        )
