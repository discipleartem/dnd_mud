# src/core/mechanics/character_generation.py
"""
Система генерации персонажей D&D.

Применяемые паттерны:
- Factory (Фабрика) — создание персонажей разными методами
- Builder (Строитель) — пошаговое создание персонажа
- Strategy (Стратегия) — разные методы генерации характеристик
- Repository (Хранилище) — загрузка конфигурации из YAML

Применяемые принципы:
- Single Responsibility — каждый класс отвечает за свою часть генерации
- Open/Closed — легко добавлять новые методы генерации
- Dependency Inversion — зависимость от абстракций
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
import yaml

from ..value_objects.dice import DiceRoll
from ..value_objects.attributes import StandardAttributes
from ..entities.character import Character
from ..entities.universal_race_factory import UniversalRaceFactory
from ..entities.class_factory import CharacterClassFactory


class GenerationMethod(Enum):
    """Методы генерации характеристик."""

    STANDARD_ARRAY = "standard_array"
    FOUR_D6_DROP_LOWEST = "four_d6_drop_lowest"
    POINT_BUY = "point_buy"


@dataclass
class GenerationConfig:
    """Конфигурация метода генерации."""

    name: str
    description: str
    method_type: GenerationMethod

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], method_type: GenerationMethod
    ) -> "GenerationConfig":
        """Создает конфигурацию из словаря."""
        return cls(
            name=data["name"], description=data["description"], method_type=method_type
        )


@dataclass
class StandardArrayConfig(GenerationConfig):
    """Конфигурация стандартного набора."""

    values: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardArrayConfig":
        """Создает конфигурацию из словаря."""
        base_config = super().from_dict(data, GenerationMethod.STANDARD_ARRAY)
        return cls(
            name=base_config.name,
            description=base_config.description,
            method_type=base_config.method_type,
            values=data["values"],
        )


@dataclass
class FourD6Config(GenerationConfig):
    """Конфигурация метода 4d6."""

    dice_count: int = 4
    drop_count: int = 1

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FourD6Config":
        """Создает конфигурацию из словаря."""
        base_config = super().from_dict(data, GenerationMethod.FOUR_D6_DROP_LOWEST)
        return cls(
            name=base_config.name,
            description=base_config.description,
            method_type=base_config.method_type,
            dice_count=data["dice_count"],
            drop_count=data["drop_count"],
        )


@dataclass
class PointBuyConfig(GenerationConfig):
    """Конфигурация покупки очков."""

    total_points: int = 27
    min_value: int = 8
    max_value: int = 15

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PointBuyConfig":
        """Создает конфигурацию из словаря."""
        base_config = super().from_dict(data, GenerationMethod.POINT_BUY)
        return cls(
            name=base_config.name,
            description=base_config.description,
            method_type=base_config.method_type,
            total_points=data["total_points"],
            min_value=data["min_value"],
            max_value=data["max_value"],
        )


class AttributeGenerator:
    """Генератор характеристик персонажа."""

    _generation_configs: Dict[GenerationMethod, GenerationConfig] = {}

    @classmethod
    def _load_configs(cls) -> None:
        """Загружает конфигурации методов генерации из YAML."""
        if cls._generation_configs:
            return

        try:
            config_path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "generation_methods.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            generation_data = config.get("generation_methods", {})

            # Стандартный набор
            if "standard_array" in generation_data:
                cls._generation_configs[GenerationMethod.STANDARD_ARRAY] = (
                    StandardArrayConfig.from_dict(generation_data["standard_array"])
                )

            # 4d6 drop lowest
            if "four_d6_drop_lowest" in generation_data:
                cls._generation_configs[GenerationMethod.FOUR_D6_DROP_LOWEST] = (
                    FourD6Config.from_dict(generation_data["four_d6_drop_lowest"])
                )

            # Покупка очков
            if "point_buy" in generation_data:
                cls._generation_configs[GenerationMethod.POINT_BUY] = (
                    PointBuyConfig.from_dict(generation_data["point_buy"])
                )

        except FileNotFoundError:
            # Fallback конфигурации
            cls._generation_configs[GenerationMethod.STANDARD_ARRAY] = (
                StandardArrayConfig(
                    "Стандартный набор",
                    "(15, 14, 13, 12, 10, 8)",
                    GenerationMethod.STANDARD_ARRAY,
                    [15, 14, 13, 12, 10, 8],
                )
            )
            cls._generation_configs[GenerationMethod.FOUR_D6_DROP_LOWEST] = (
                FourD6Config(
                    "4d6",
                    "Бросок 4d6, отбрасываем наименьший",
                    GenerationMethod.FOUR_D6_DROP_LOWEST,
                    4,
                    1,
                )
            )
            cls._generation_configs[GenerationMethod.POINT_BUY] = PointBuyConfig(
                "Покупка очков",
                "Распределение очков по выбору (27 очков)",
                GenerationMethod.POINT_BUY,
                27,
                8,
                15,
            )

    @classmethod
    def generate_standard_array(cls) -> Dict[str, int]:
        """Генерирует характеристики стандартным набором."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.STANDARD_ARRAY]

        if not isinstance(config, StandardArrayConfig):
            raise ValueError("Неверная конфигурация для стандартного набора")

        values = config.values.copy()
        random.shuffle(values)

        attributes = {}
        for attr_name in StandardAttributes.get_all().keys():
            if not values:
                break
            attributes[attr_name] = values.pop()

        return attributes

    @classmethod
    def generate_four_d6_drop_lowest(cls) -> Dict[str, int]:
        """Генерирует характеристики методом 4d6 drop lowest."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.FOUR_D6_DROP_LOWEST]

        if not isinstance(config, FourD6Config):
            raise ValueError("Неверная конфигурация для метода 4d6")

        attributes = {}
        for attr_name in StandardAttributes.get_all().keys():
            rolls = DiceRoll.roll_multiple("d6", config.dice_count)
            roll_values = [roll.value for roll in rolls]
            roll_values.sort(reverse=True)
            # Отбрасываем наименьшие
            final_rolls = roll_values[: config.dice_count - config.drop_count]
            attributes[attr_name] = sum(final_rolls)

        return attributes

    @classmethod
    def get_point_buy_costs(cls) -> Dict[int, int]:
        """Возвращает стоимость очков для покупки характеристик."""
        # Стандартная таблица стоимости D&D 5e
        return {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}

    @classmethod
    def validate_point_buy_attributes(cls, attributes: Dict[str, int]) -> bool:
        """Проверяет валидность характеристик для покупки очков."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.POINT_BUY]

        if not isinstance(config, PointBuyConfig):
            return False

        # Проверяем диапазоны
        for value in attributes.values():
            if not (config.min_value <= value <= config.max_value):
                return False

        # Проверяем общую стоимость
        total_cost = sum(
            cls.get_point_buy_costs().get(value, 999) for value in attributes.values()
        )
        return total_cost <= config.total_points

    @classmethod
    def get_point_buy_remaining_points(cls, attributes: Dict[str, int]) -> int:
        """Возвращает оставшиеся очки для покупки."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.POINT_BUY]

        if not isinstance(config, PointBuyConfig):
            return 0

        total_cost = sum(
            cls.get_point_buy_costs().get(value, 999) for value in attributes.values()
        )
        return config.total_points - total_cost

    @classmethod
    def get_available_methods(cls) -> List[GenerationConfig]:
        """Возвращает доступные методы генерации."""
        cls._load_configs()
        return list(cls._generation_configs.values())

    @classmethod
    def get_standard_array_values(cls) -> List[int]:
        """Возвращает значения стандартного набора для распределения."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.STANDARD_ARRAY]

        if not isinstance(config, StandardArrayConfig):
            raise ValueError("Неверная конфигурация для стандартного набора")

        return config.values.copy()

    @classmethod
    def validate_standard_array_assignment(cls, attributes: Dict[str, int]) -> bool:
        """Проверяет валидность распределения значений стандартного набора."""
        cls._load_configs()
        config = cls._generation_configs[GenerationMethod.STANDARD_ARRAY]

        if not isinstance(config, StandardArrayConfig):
            return False

        # Проверяем, что все характеристики присутствуют
        required_attrs = set(StandardAttributes.get_all().keys())
        provided_attrs = set(attributes.keys())
        
        if provided_attrs != required_attrs:
            return False

        # Проверяем, что используем ровно те значения, что в стандартном наборе
        expected_values = sorted(config.values)
        actual_values = sorted(attributes.values())
        
        return expected_values == actual_values


class CharacterBuilder:
    """Строитель персонажа для пошагового создания."""

    def __init__(self):
        """Инициализирует билдер."""
        self.reset()

    def reset(self) -> "CharacterBuilder":
        """Сбрасывает билдер в начальное состояние."""
        self._name: str = "Безымянный"
        self._level: int = 1
        self._race_name: str = "human"
        self._class_name: str = "fighter"
        self._attributes: Dict[str, int] = {}
        self._generation_method: Optional[GenerationMethod] = None
        self._skills_proficiencies: List[str] = []
        return self

    def set_name(self, name: str) -> "CharacterBuilder":
        """Устанавливает имя персонажа."""
        self._name = name
        return self

    def set_level(self, level: int) -> "CharacterBuilder":
        """Устанавливает уровень персонажа."""
        if level < 1:
            raise ValueError(f"Уровень должен быть не менее 1, получено: {level}")
        self._level = level
        return self

    def set_race(self, race_name: str) -> "CharacterBuilder":
        """Устанавливает расу персонажа.
        
        Args:
            race_name: Ключ расы в формате "race" или "race.subrace"
        """
        self._race_name = race_name
        return self

    def set_class(self, class_name: str) -> "CharacterBuilder":
        """Устанавливает класс персонажа."""
        self._class_name = class_name
        return self

    def generate_attributes_standard_array(self) -> "CharacterBuilder":
        """Генерирует характеристики стандартным набором."""
        self._attributes = AttributeGenerator.generate_standard_array()
        self._generation_method = GenerationMethod.STANDARD_ARRAY
        return self

    def generate_attributes_four_d6(self) -> "CharacterBuilder":
        """Генерирует характеристики методом 4d6 drop lowest."""
        self._attributes = AttributeGenerator.generate_four_d6_drop_lowest()
        self._generation_method = GenerationMethod.FOUR_D6_DROP_LOWEST
        return self

    def set_attributes_point_buy(
        self, attributes: Dict[str, int]
    ) -> "CharacterBuilder":
        """Устанавливает характеристики методом покупки очков."""
        if not AttributeGenerator.validate_point_buy_attributes(attributes):
            raise ValueError("Невалидные характеристики для покупки очков")
        self._attributes = attributes.copy()
        self._generation_method = GenerationMethod.POINT_BUY
        return self

    def set_attributes_manual(self, attributes: Dict[str, int]) -> "CharacterBuilder":
        """Устанавливает характеристики вручную (для отладки)."""
        self._attributes = attributes.copy()
        self._generation_method = None
        return self

    def set_attributes_standard_array_manual(
        self, attributes: Dict[str, int]
    ) -> "CharacterBuilder":
        """Устанавливает характеристики методом стандартного набора с ручным распределением."""
        if not AttributeGenerator.validate_standard_array_assignment(attributes):
            raise ValueError("Невалидное распределение значений стандартного набора")
        
        self._attributes = attributes.copy()
        self._generation_method = GenerationMethod.STANDARD_ARRAY
        return self

    def add_skill_proficiency(self, skill_name: str) -> "CharacterBuilder":
        """Добавляет владение навыком."""
        if skill_name not in self._skills_proficiencies:
            self._skills_proficiencies.append(skill_name)
        return self

    def build(self) -> Character:
        """Создает персонажа."""
        if not self._attributes:
            raise ValueError("Характеристики не установлены")

        # Создаем расу и класс с поддержкой подрас
        if "." in self._race_name:
            # Формат "race.subrace"
            race_key, subrace_key = self._race_name.split(".", 1)
            race = UniversalRaceFactory.create_race(race_key, subrace_key)
        else:
            # Формат "race"
            race = UniversalRaceFactory.create_race(self._race_name)
            
        character_class = CharacterClassFactory.create_class(self._class_name)

        # Создаем персонажа
        character = Character(
            name=self._name,
            level=self._level,
            race=race,
            character_class=character_class,
        )

        # Устанавливаем характеристики
        for attr_name, value in self._attributes.items():
            if hasattr(character, attr_name):
                attr = getattr(character, attr_name)
                attr.value = value

        # Применяем расовые бонусы
        character.apply_race_bonuses()

        # Рассчитываем производные характеристики
        character.calculate_derived_stats()

        # Добавляем владения навыками
        for skill_name in self._skills_proficiencies:
            character.add_skill_proficiency(skill_name)

        return character


class CharacterFactory:
    """Фабрика для создания персонажей разными методами."""

    @staticmethod
    def create_random_character(name: str = "Безымянный", level: int = 1) -> Character:
        """Создает персонажа со случайными характеристиками."""
        builder = CharacterBuilder()
        return (
            builder.set_name(name)
            .set_level(level)
            .generate_attributes_four_d6()
            .build()
        )

    @staticmethod
    def create_standard_character(
        name: str = "Безымянный", level: int = 1
    ) -> Character:
        """Создает персонажа со стандартным набором характеристик."""
        builder = CharacterBuilder()
        return (
            builder.set_name(name)
            .set_level(level)
            .generate_attributes_standard_array()
            .build()
        )

    @staticmethod
    def create_optimized_character(
        name: str = "Безымянный",
        level: int = 1,
        race_name: str = "human",
        class_name: str = "fighter",
    ) -> Character:
        """Создает оптимизированного персонажа под класс."""
        builder = CharacterBuilder()
        return (
            builder.set_name(name)
            .set_level(level)
            .set_race(race_name)
            .set_class(class_name)
            .generate_attributes_standard_array()
            .build()
        )


# Пример использования
if __name__ == "__main__":
    # Создаем персонажа с разными методами
    print("=== Случайный персонаж (4d6) ===")
    random_char = CharacterFactory.create_random_character("Гром")
    print(f"Имя: {random_char.name}")
    print(
        f"Сила: {random_char.strength.value} (+{random_char.get_ability_modifier(random_char.strength.value)})"
    )
    print(
        f"Ловкость: {random_char.dexterity.value} (+{random_char.get_ability_modifier(random_char.dexterity.value)})"
    )
    print(
        f"Телосложение: {random_char.constitution.value} (+{random_char.get_ability_modifier(random_char.constitution.value)})"
    )

    print("\n=== Стандартный персонаж ===")
    standard_char = CharacterFactory.create_standard_character("Эльра")
    print(f"Имя: {standard_char.name}")
    print(f"Сила: {standard_char.strength.value}")
    print(f"Ловкость: {standard_char.dexterity.value}")
    print(f"Телосложение: {standard_char.constitution.value}")

    print("\n=== Доступные методы генерации ===")
    for method in AttributeGenerator.get_available_methods():
        print(f"- {method.name}: {method.description}")
