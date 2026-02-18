"""Система генерации персонажей D&D."""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

from ..value_objects.dice import Dice
from ..entities.character import Character
from ..entities.universal_race_factory import UniversalRaceFactory
from ..entities.class_factory import CharacterClassFactory


class GenerationMethod(Enum):
    """Методы генерации характеристик."""
    STANDARD_ARRAY = "standard_array"
    FOUR_D6_DROP_LOWEST = "four_d6_drop_lowest"
    POINT_BUY = "point_buy"


class CharacterGenerator:
    """Простой генератор персонажей."""
    
    @staticmethod
    def generate_attributes(method: GenerationMethod = GenerationMethod.STANDARD_ARRAY) -> Dict[str, int]:
        """Генерирует характеристики."""
        if method == GenerationMethod.STANDARD_ARRAY:
            return {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8,
            }
        elif method == GenerationMethod.FOUR_D6_DROP_LOWEST:
            attributes = {}
            for attr in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.sort()
                attributes[attr] = sum(rolls[1:])  # Отбрасываем самый низкий
            return attributes
        else:  # POINT_BUY
            return {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            }
    
    @staticmethod
    def create_character(
        name: str = "Безымянный",
        race_name: str = "human",
        class_name: str = "fighter",
        generation_method: GenerationMethod = GenerationMethod.STANDARD_ARRAY
    ) -> Character:
        """Создает нового персонажа."""
        # Генерируем характеристики
        attributes = CharacterGenerator.generate_attributes(generation_method)
        
        # Создаем расу и класс
        race = UniversalRaceFactory.create_race(race_name)
        character_class = CharacterClassFactory.create_class(class_name)
        
        # Создаем персонажа
        character = Character(
            name=name,
            race=race,
            character_class=character_class,
            **attributes
        )
        
        # Применяем расовые бонусы
        character.apply_race_bonuses()
        
        # Рассчитываем производные характеристики
        character.calculate_derived_stats()
        
        return character
