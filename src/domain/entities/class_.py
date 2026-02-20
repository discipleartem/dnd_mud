# src/domain/entities/class_.py
"""Класс персонажа D&D 5e."""

from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional, TypedDict, Any
from ..interfaces.localization import get_text


class ClassData(TypedDict):
    """Данные класса для сериализации."""

    name: str
    display_name: str
    description: str
    primary_ability: str
    hit_die: str
    saving_throws: List[str]
    armor_proficiencies: List[str]
    weapon_proficiencies: List[str]
    level: int
    spellcasting: Dict[str, Union[str, int, List[int], List[str], bool, None]]
    divine_domain: Optional[str]
    skills: Dict[str, Union[str, int, bool]]
    subclasses: List[Dict[str, Union[str, int]]]
    features: List[Dict[str, Union[str, int]]]


class SpellcastingData(TypedDict):
    """Данные заклинаний."""

    ability: str
    spell_list: List[str]
    cantrips: List[str]
    spells_per_day: Dict[str, Union[int, List[int]]]
    ritual_casting: bool
    spell_ability: str
    prepared_spells: bool
    known_spells: Optional[List[str]]
    extra_attacks: Optional[List[str]]


@dataclass
class CharacterClass:
    """Класс персонажа D&D."""

    name: str
    display_name: str = ""
    description: str = ""
    primary_ability: str = ""
    hit_die: str = "d8"
    saving_throws: List[str] = field(default_factory=list)
    armor_proficiencies: List[str] = field(default_factory=list)
    weapon_proficiencies: List[str] = field(default_factory=list)
    level: int = 1
    spellcasting: Dict[str, Union[str, int, List[int], List[str], bool, None]] = field(
        default_factory=dict
    )
    divine_domain: Optional[str] = None
    skills: Dict[str, Union[str, int, bool]] = field(default_factory=dict)
    subclasses: List[Dict[str, Union[str, int]]] = field(default_factory=list)
    features: List[Dict[str, Union[str, int]]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Инициализация после создания."""
        if not self.display_name:
            self.display_name = self.name

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название класса."""
        return get_text(f"class_name.{self.name}")

    @property
    def localized_description(self) -> str:
        """Возвращает локализованное описание."""
        return get_text(f"class_description.{self.name}")

    @property
    def hit_points_at_level(self) -> int:
        """Возвращает базовые хиты на уровне."""
        # Базовые хиты = максимум hit_die + модификатор телосложения * (уровень - 1)
        die_max = int(self.hit_die[1:])  # Извлекаем число из "d8", "d10" и т.д.
        return die_max + (die_max + 1) // 2 * (self.level - 1)

    def get_saving_throws(self) -> List[str]:
        """Возвращает спасброски класса."""
        return self.saving_throws.copy()

    def has_proficiency(self, proficiency_type: str, item: str) -> bool:
        """Проверяет наличие владения."""
        if proficiency_type == "armor":
            return item in self.armor_proficiencies
        elif proficiency_type == "weapon":
            return item in self.weapon_proficiencies
        return False

    def add_proficiency(self, proficiency_type: str, item: str) -> None:
        """Добавляет владение."""
        if proficiency_type == "armor" and item not in self.armor_proficiencies:
            self.armor_proficiencies.append(item)
        elif proficiency_type == "weapon" and item not in self.weapon_proficiencies:
            self.weapon_proficiencies.append(item)

    def remove_proficiency(self, proficiency_type: str, item: str) -> None:
        """Удаляет владение."""
        if proficiency_type == "armor" and item in self.armor_proficiencies:
            self.armor_proficiencies.remove(item)
        elif proficiency_type == "weapon" and item in self.weapon_proficiencies:
            self.weapon_proficiencies.remove(item)

    def level_up(self) -> None:
        """Повышает уровень."""
        self.level += 1

    def get_proficiency_bonus(self) -> int:
        """Возвращает бонус мастерства для класса."""
        # Бонус мастерства в 5e: 1-4 lvl: +2, 5-8: +3, 9-12: +4, 13-16: +5, 17-20: +6
        if self.level <= 4:
            return 2
        elif self.level <= 8:
            return 3
        elif self.level <= 12:
            return 4
        elif self.level <= 16:
            return 5
        else:
            return 6

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует класс в словарь."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "primary_ability": self.primary_ability,
            "hit_die": self.hit_die,
            "saving_throws": self.saving_throws,
            "armor_proficiencies": self.armor_proficiencies,
            "weapon_proficiencies": self.weapon_proficiencies,
            "level": self.level,
            "spellcasting": self.spellcasting,
            "divine_domain": self.divine_domain,
            "skills": self.skills,
            "subclasses": self.subclasses,
            "features": self.features,
        }

    @classmethod
    def from_dict(cls, data: ClassData) -> "CharacterClass":
        """Создает класс из словаря."""
        # Преобразуем общие данные в конкретные типы
        saving_throws = data.get("saving_throws", [])
        if not isinstance(saving_throws, list):
            saving_throws = []

        armor_proficiencies = data.get("armor_proficiencies", [])
        if not isinstance(armor_proficiencies, list):
            armor_proficiencies = []

        weapon_proficiencies = data.get("weapon_proficiencies", [])
        if not isinstance(weapon_proficiencies, list):
            weapon_proficiencies = []

        skills = data.get("skills", {})
        if not isinstance(skills, dict):
            skills = {}

        subclasses = data.get("subclasses", [])
        if not isinstance(subclasses, list):
            subclasses = []

        features = data.get("features", [])
        if not isinstance(features, list):
            features = []

        spellcasting = data.get(
            "spellcasting",
            {
                "ability": "",
                "spell_list": [],
                "cantrips": [],
                "spells_per_day": {},
                "ritual_casting": False,
                "spell_ability": "",
                "prepared_spells": False,
                "known_spells": None,
                "extra_attacks": None,
            },
        )

        return cls(
            name=str(data.get("name", "")),
            display_name=str(data.get("display_name", "")),
            description=str(data.get("description", "")),
            primary_ability=str(data.get("primary_ability", "")),
            hit_die=str(data.get("hit_die", "d8")),
            saving_throws=saving_throws,
            armor_proficiencies=armor_proficiencies,
            weapon_proficiencies=weapon_proficiencies,
            level=int(data.get("level", 1)),
            spellcasting=spellcasting,
            divine_domain=data.get("divine_domain"),
            skills=skills,
            subclasses=subclasses,
            features=features,
        )

    def __str__(self) -> str:
        """Строковое представление."""
        return f"{self.localized_name} ({self.level} уровень)"

    def __repr__(self) -> str:
        """Полное строковое представление."""
        return f"CharacterClass(name='{self.name}', level={self.level})"
