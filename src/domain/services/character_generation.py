# src/domain/services/character_generation.py
"""Сервис генерации персонажей."""

from dataclasses import dataclass, field
from typing import Dict, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from ..entities.character import Character


class GenerationMethod(Enum):
    """Методы генерации характеристик."""

    STANDARD_ARRAY = "standard_array"
    FOUR_D6_DROP_LOWEST = "four_d6_drop_lowest"
    POINT_BUY = "point_buy"


@dataclass
class CharacterGenerator:
    """Генератор персонажей."""

    name: str
    race_name: str
    class_name: str
    level: int = 1
    attributes: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def generate_attributes(cls, method: GenerationMethod) -> Dict[str, int]:
        """Генерирует характеристики указанным методом."""
        generator = cls("temp", "human", "fighter")

        if method == GenerationMethod.STANDARD_ARRAY:
            return generator.generate_standard_array()
        elif method == GenerationMethod.FOUR_D6_DROP_LOWEST:
            return generator.generate_four_d6()
        elif method == GenerationMethod.POINT_BUY:
            return generator.generate_point_buy()
        else:
            return generator.generate_standard_array()

    @classmethod
    def create_character(
        cls,
        name: str,
        race_name: str,
        class_name: str,
        generation_method: GenerationMethod = GenerationMethod.STANDARD_ARRAY,
        level: int = 1,
    ) -> "Character":
        """Создает нового персонажа."""
        if TYPE_CHECKING:
            from ..entities.character import Character
        from ..entities.universal_race_factory import UniversalRaceFactory
        from ..entities.class_factory import CharacterClassFactory

        # Генерируем характеристики
        attributes = cls.generate_attributes(generation_method)

        # Создаем расу и класс
        race = UniversalRaceFactory.create_race(race_name)
        character_class = CharacterClassFactory.create_class(class_name)

        # Создаем персонажа
        character = Character(
            name=name, race=race, character_class=character_class, level=level
        )

        # Применяем характеристики
        for attr_name, value in attributes.items():
            if hasattr(character, attr_name):
                getattr(character, attr_name).value = value

        return character

    def generate_point_buy(self) -> Dict[str, int]:
        """Генерирует характеристики методом покупки очков."""
        # Простая реализация - все по 10
        return {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
        }

    @classmethod
    def create_standard_character(
        cls, name: str = "Безымянный"
    ) -> "CharacterGenerator":
        """Создает персонажа со стандартными характеристиками."""
        return cls(
            name=name,
            race_name="human",
            class_name="fighter",
            level=1,
            attributes={
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            },
        )

    def generate_standard_array(self) -> Dict[str, int]:
        """Генерирует стандартный набор характеристик."""
        standard_values = [15, 14, 13, 12, 10, 8]
        attributes = {}

        for i, attr in enumerate(
            [
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ]
        ):
            attributes[attr] = standard_values[i]

        return attributes

    def generate_four_d6(self) -> Dict[str, int]:
        """Генерирует характеристики методом 4d6."""
        import random

        attributes = {}
        for attr in [
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        ]:
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort()
            value = sum(rolls[1:])  # Отбрасываем наименьший
            attributes[attr] = max(3, min(20, value))

        return attributes

    def get_available_methods(self) -> List[GenerationMethod]:
        """Возвращает доступные методы генерации."""
        return list(GenerationMethod)
