# src/domain/entities/character.py
"""Персонаж D&D 5e."""

from dataclasses import dataclass, field
from typing import Dict, List, Union, TypedDict, Any
from .attribute import Attribute
from .race import Race, RaceData
from .class_ import CharacterClass, ClassData


class CharacterData(TypedDict):
    """Данные персонажа."""

    name: str
    race: RaceData
    character_class: ClassData
    level: int
    attributes: Dict[str, Dict[str, Union[str, int]]]
    hp_max: int
    hp_current: int
    ac: int
    gold: int


@dataclass
class Character:
    """Персонаж D&D."""

    name: str
    race: Race
    character_class: CharacterClass
    level: int = 1
    attributes: Dict[str, Attribute] = field(default_factory=dict)
    hp_max: int = 0
    hp_current: int = 0
    ac: int = 10
    gold: int = 0

    def __post_init__(self) -> None:
        """Инициализация после создания."""
        if not self.attributes:
            self._initialize_attributes()

        if self.hp_max == 0:
            self._calculate_hp_max()

        if self.hp_current == 0:
            self.hp_current = self.hp_max

        if self.ac == 10:
            self._calculate_ac()

    def _initialize_attributes(self) -> None:
        """Инициализирует характеристики персонажа."""
        base_attributes = [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]

        for attr_name in base_attributes:
            # Применяем бонусы расы
            base_value = 10 + self.race.get_attribute_bonus(attr_name)
            self.attributes[attr_name] = Attribute(name=attr_name, value=base_value)

    def _calculate_hp_max(self) -> None:
        """Рассчитывает максимальные хиты."""
        # Базовые хиты от класса
        class_hp = self.character_class.hit_points_at_level

        # Модификатор телосложения
        con_mod = self.get_attribute_modifier("constitution")

        # Общие хиты
        self.hp_max = class_hp + (con_mod * self.level)

    def _calculate_ac(self) -> None:
        """Рассчитывает класс брони."""
        # Базовый AC = 10 + модификатор ловкости
        dex_mod = self.get_attribute_modifier("dexterity")
        self.ac = 10 + dex_mod

    def get_attribute_value(self, attribute_name: str) -> int:
        """Возвращает значение характеристики."""
        if attribute_name not in self.attributes:
            raise ValueError(f"Неизвестная характеристика: {attribute_name}")
        return self.attributes[attribute_name].value

    def get_attribute_modifier(self, attribute_name: str) -> int:
        """Возвращает модификатор характеристики."""
        value = self.get_attribute_value(attribute_name)
        return (value - 10) // 2

    def get_all_modifiers(self) -> Dict[str, int]:
        """Возвращает модификаторы всех характеристик."""
        return {
            attr_name: self.get_attribute_modifier(attr_name)
            for attr_name in self.attributes
        }

    def get_proficiency_bonus(self) -> int:
        """Возвращает бонус мастерства."""
        return self.character_class.get_proficiency_bonus()

    def level_up(self) -> None:
        """Повышает уровень персонажа."""
        self.level += 1
        self.character_class.level_up()
        self._calculate_hp_max()
        # Восстанавливаем хиты при повышении уровня
        self.hp_current = self.hp_max

    def take_damage(self, damage: int) -> int:
        """Получает урон."""
        actual_damage = min(damage, self.hp_current)
        self.hp_current -= actual_damage
        return actual_damage

    def heal(self, amount: int) -> int:
        """Лечит персонажа."""
        actual_heal = min(amount, self.hp_max - self.hp_current)
        self.hp_current += actual_heal
        return actual_heal

    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.hp_current > 0

    def get_saving_throws(self) -> List[str]:
        """Возвращает спасброски персонажа."""
        return self.character_class.get_saving_throws()

    def has_saving_throw_proficiency(self, save_name: str) -> bool:
        """Проверяет владение спасброском."""
        return save_name in self.get_saving_throws()

    def get_ability_modifier(self, value: int) -> int:
        """Возвращает модификатор характеристики."""
        return (value - 10) // 2

    @property
    def strength(self) -> Attribute:
        """Возвращает характеристику Силы."""
        return self.attributes.get("strength", Attribute("strength", 10))

    @property
    def dexterity(self) -> Attribute:
        """Возвращает характеристику Ловкости."""
        return self.attributes.get("dexterity", Attribute("dexterity", 10))

    @property
    def constitution(self) -> Attribute:
        """Возвращает характеристику Телосложения."""
        return self.attributes.get("constitution", Attribute("constitution", 10))

    @property
    def intelligence(self) -> Attribute:
        """Возвращает характеристику Интеллекта."""
        return self.attributes.get("intelligence", Attribute("intelligence", 10))

    @property
    def wisdom(self) -> Attribute:
        """Возвращает характеристику Мудрости."""
        return self.attributes.get("wisdom", Attribute("wisdom", 10))

    @property
    def charisma(self) -> Attribute:
        """Возвращает характеристику Харизмы."""
        return self.attributes.get("charisma", Attribute("charisma", 10))

    def calculate_derived_stats(self) -> None:
        """Рассчитывает производные характеристики."""
        self._calculate_hp_max()
        self._calculate_ac()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь для сериализации."""
        race_dict = self.race.to_dict()
        class_dict = self.character_class.to_dict()

        return {
            "name": self.name,
            "race": race_dict,
            "character_class": class_dict,
            "level": self.level,
            "attributes": {k: v.__dict__ for k, v in self.attributes.items()},
            "hp_max": self.hp_max,
            "hp_current": self.hp_current,
            "ac": self.ac,
            "gold": self.gold,
        }

    @classmethod
    def from_dict(cls, data: CharacterData) -> "Character":
        """Создает персонажа из словаря."""
        # Конвертируем словари в объекты
        race_data = data["race"]
        class_data = data["character_class"]

        race_obj = Race.from_dict(race_data)
        class_obj = CharacterClass.from_dict(class_data)

        return cls(
            name=data["name"],
            race=race_obj,
            character_class=class_obj,
            level=data["level"],
            hp_max=data["hp_max"],
            hp_current=data["hp_current"],
            ac=data["ac"],
            gold=data["gold"],
        )

    def __str__(self) -> str:
        """Строковое представление."""
        return f"{self.name} - {self.race.name} {self.character_class.name} ({self.level} уровень)"

    def __repr__(self) -> str:
        """Полное строковое представление."""
        return f"Character(name='{self.name}', race='{self.race.name}', class='{self.character_class.name}', level={self.level})"
