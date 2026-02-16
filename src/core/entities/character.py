"""
Модуль персонажа D&D MUD.

Определяет базовый класс персонажа и его характеристики.
"""

from dataclasses import dataclass, field
from typing import Dict
from ..mechanics.attributes import StandardAttributes
from .attribute import Attribute
from .race import Race
from .race_factory import RaceFactory


@dataclass
class Character:
    """Класс персонажа D&D."""
    
    # Базовая информация
    name: str = field(default="Безымянный")
    level: int = field(default=1, min=1)
    race: Race = field(default_factory=lambda: RaceFactory.create_race("human"))
    character_class: str = field(default="Воин")
    
    # Характеристики
    strength: Attribute = field(default_factory=lambda: Attribute("strength", 10))
    dexterity: Attribute = field(default_factory=lambda: Attribute("dexterity", 10))
    constitution: Attribute = field(default_factory=lambda: Attribute("constitution", 10))
    intelligence: Attribute = field(default_factory=lambda: Attribute("intelligence", 10))
    wisdom: Attribute = field(default_factory=lambda: Attribute("wisdom", 10))
    charisma: Attribute = field(default_factory=lambda: Attribute("charisma", 10))


    def __post_init__(self) -> None:
            """Создает стандартные характеристики."""
            for attr_name, standard_attr in StandardAttributes.get_all().items():
                attribute = Attribute(attr_name, standard_attr.default_value)
                setattr(self, attr_name, attribute)


    def __getattr__(self, name: str) -> int:
            """Динамический доступ к характеристикам."""
            # Ищем в стандартах
            for attr_name, standard_attr in StandardAttributes.get_all().items():
                if standard_attr.short_name == name:
                    return getattr(self, attr_name).value
            
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


    def __setattr__(self, name: str, value: int) -> None:
        """Динамическая запись характеристик."""
        if name in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
            attribute_map = {
                'STR': 'strength', 'DEX': 'dexterity', 'CON': 'constitution',
                'INT': 'intelligence', 'WIS': 'wisdom', 'CHA': 'charisma'
            }
            getattr(self, attribute_map[name]).value = value
        else:
            super().__setattr__(name, value)
    
    def apply_race_bonuses(self) -> None:
        """Применяет расовые бонусы к характеристикам."""
        attributes = {
            'strength': self.strength.value,
            'dexterity': self.dexterity.value,
            'constitution': self.constitution.value,
            'intelligence': self.intelligence.value,
            'wisdom': self.wisdom.value,
            'charisma': self.charisma.value
        }
        
        boosted_attributes = self.race.apply_bonuses(attributes)
        
        # Обновляем значения характеристик
        for attr_name, value in boosted_attributes.items():
            getattr(self, attr_name).value = value
    
    def get_ability_modifier(self, value: int) -> int:
        """Рассчитывает модификатор характеристики.
        
        Args:
            value: Значение характеристики
            
        Returns:
            Модификатор (значение - 10) // 2
        """
        return (value - 10) // 2
    
    def get_all_modifiers(self) -> Dict[str, int]:
        """Возвращает словарь всех модификаторов характеристик."""
        return {
            'strength': self.get_ability_modifier(self.strength.value),
            'dexterity': self.get_ability_modifier(self.dexterity.value),
            'constitution': self.get_ability_modifier(self.constitution.value),
            'intelligence': self.get_ability_modifier(self.intelligence.value),
            'wisdom': self.get_ability_modifier(self.wisdom.value),
            'charisma': self.get_ability_modifier(self.charisma.value)
        }