# src/domain/entities/race.py
"""Раса персонажа D&D 5e."""

from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional, TypedDict, Any
from ..interfaces.localization import get_text


class RaceData(TypedDict):
    """Данные расы для сериализации."""

    name: str
    display_name: str
    description: str
    bonuses: Dict[str, int]
    features: "List[RaceFeature]"
    size: str
    speed: int
    languages: List[str]
    subraces: Dict[str, Any]
    alternative_features: "Optional[AlternativeFeature]"


class RaceFeature(TypedDict):
    """Особенность расы."""

    name: str
    description: str
    type: Optional[str]
    bonus_value: Optional[int]
    max_choices: Optional[int]
    choices: Optional[List[str]]


class AlternativeFeature(TypedDict):
    """Альтернативная особенность."""

    ability_choice: Optional[Dict[str, Union[str, int]]]
    skill_choice: Optional[Dict[str, Union[str, int]]]
    feat_choice: Optional[Dict[str, Union[str, int]]]
    traits: Optional[List[Dict[str, str]]]
    proficiencies: Optional[List[Dict[str, Union[str, List[str]]]]]
    name: Optional[str]
    description: Optional[str]
    type: Optional[str]


@dataclass
class Race:
    """Раса персонажа D&D."""

    name: str
    display_name: str = ""
    description: str = ""
    bonuses: Dict[str, int] = field(default_factory=dict)
    features: List[RaceFeature] = field(default_factory=list)
    size: str = "medium"
    speed: int = 30
    languages: List[str] = field(default_factory=list)
    subraces: Dict[str, "Race"] = field(default_factory=dict)
    alternative_features: Optional[AlternativeFeature] = None

    def __post_init__(self) -> None:
        """Инициализация после создания."""
        if not self.display_name:
            self.display_name = self.name

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название расы."""
        return get_text(f"race_name.{self.name}")

    @property
    def localized_description(self) -> str:
        """Возвращает локализованное описание."""
        return get_text(f"race_description.{self.name}")

    def get_attribute_bonus(self, attribute: str) -> int:
        """Возвращает бонус к характеристике."""
        return self.bonuses.get(attribute, 0)

    def get_all_bonuses(self) -> Dict[str, int]:
        """Возвращает все бонусы расы."""
        return self.bonuses.copy()

    def has_feature(self, feature_name: str) -> bool:
        """Проверяет наличие особенности."""
        return any(feature.get("name") == feature_name for feature in self.features)

    def get_feature(self, feature_name: str) -> Optional[RaceFeature]:
        """Возвращает особенности по имени."""
        for feature in self.features:
            if feature.get("name") == feature_name:
                return feature
        return None

    def get_all_features(self) -> List[RaceFeature]:
        """Возвращает все особенности расы."""
        return self.features.copy()

    def add_bonus(self, attribute: str, bonus: int) -> None:
        """Добавляет бонус к характеристике."""
        self.bonuses[attribute] = self.bonuses.get(attribute, 0) + bonus

    def add_feature(self, feature: RaceFeature) -> None:
        """Добавляет особенность."""
        self.features.append(feature)

    def apply_bonuses(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """Применяет бонусы расы к характеристикам."""
        result = attributes.copy()
        for attr, bonus in self.bonuses.items():
            result[attr] = result.get(attr, 10) + bonus
        return result

    def apply_alternative_bonuses(
        self, attributes: Dict[str, int], choices: Dict[str, Union[str, int, List[str]]]
    ) -> Dict[str, int]:
        """Применяет альтернативные бонусы расы (для людей)."""
        result = attributes.copy()

        if "ability_scores" in choices:
            ability_scores = choices["ability_scores"]
            if isinstance(ability_scores, list):
                for attr in ability_scores:
                    if attr in result:
                        result[attr] += 1

        return result

    def get_alternative_options(
        self,
    ) -> Dict[str, Dict[str, Union[str, int, List[str]]]]:
        """Возвращает альтернативные опции для расы."""
        if not self.alternative_features:
            return {}

        return {
            "ability_bonus": {
                "name": "Увеличение характеристик",
                "description": "Выберите две характеристики для увеличения на +1",
                "type": "ability_bonus",
                "max_choices": 2,
                "allowed_attributes": [
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ],
            },
            "skill": {
                "name": "Владение навыком",
                "description": "Получите владение одним навыком",
                "type": "skill",
            },
            "feat": {
                "name": "Черта",
                "description": "Получите одну черту",
                "type": "feat",
            },
        }

    def to_dict(self) -> Dict[str, Union[str, int, List[str], list, dict]]:
        """Преобразует в словарь для сериализации."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "bonuses": self.bonuses,
            "features": self.features,
            "size": self.size,
            "speed": self.speed,
            "languages": self.languages,
        }

    @classmethod
    def from_dict(cls, data: RaceData) -> "Race":
        """Создает расу из словаря."""
        # Преобразуем общие данные в конкретные типы
        features = data.get("features", [])
        if not isinstance(features, list):
            features = []

        bonuses = data.get("bonuses", {})
        if not isinstance(bonuses, dict):
            bonuses = {}
        else:
            # Фильтруем только целочисленные значения
            bonuses = {
                k: int(v)
                for k, v in bonuses.items()
                if isinstance(v, (int, str)) and str(v).isdigit()
            }

        return cls(
            name=str(data.get("name", "")),
            display_name=str(data.get("display_name", "")),
            description=str(data.get("description", "")),
            bonuses=bonuses,
            features=features,
            size=str(data.get("size", "medium")),
            speed=int(data.get("speed", 30)),
            languages=list(data.get("languages", [])),
        )

    def __str__(self) -> str:
        """Строковое представление."""
        return self.localized_name

    def __repr__(self) -> str:
        """Полное строковое представление."""
        return f"Race(name='{self.name}', bonuses={self.bonuses})"
