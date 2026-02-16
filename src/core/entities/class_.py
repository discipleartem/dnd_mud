"""
Модуль классов D&D MUD.

Определяет класс персонажа и их бонусы к характеристикам.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CharacterClass:
    """Класс персонажа D&D."""
    
    name: str
    description: str
    bonuses: Dict[str, int]
    hit_die: str = "d10"  # Кубик для HP
    
    def apply_bonuses(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """Применяет классовые бонусы к характеристикам.
        
        Args:
            attributes: Исходные характеристики персонажа
            
        Returns:
            Характеристики с примененными бонусами
        """
        result = attributes.copy()
        
        for attr_name, bonus in self.bonuses.items():
            if attr_name in result:
                result[attr_name] += bonus
        
        return result
    
    def calculate_hp(self, constitution: int) -> int:
        """Рассчитывает максимальное HP.
        
        Args:
            constitution: Значение телосложения
            
        Returns:
            Максимальное количество очков здоровья
        """
        import re
        
        # Извлекаем число из строки типа "d10"
        match = re.search(r'd(\d+)', self.hit_die)
        if match:
            hit_die_value = int(match.group(1))
            # HP = hit_die + модификатор телосложения
            con_modifier = (constitution - 10) // 2
            return hit_die_value + con_modifier
        
        return 10 + (constitution - 10) // 2  # Значение по умолчанию
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterClass':
        """Создает класс из словаря.
        
        Args:
            data: Словарь с данными класса
            
        Returns:
            Объект класса персонажа
        """
        return cls(
            name=data.get('name', 'Безымянный класс'),
            description=data.get('description', ''),
            bonuses=data.get('bonuses', {}),
            hit_die=data.get('hit_die', 'd10')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует класс в словарь.
        
        Returns:
            Словарь с данными класса
        """
        return {
            'name': self.name,
            'description': self.description,
            'bonuses': self.bonuses,
            'hit_die': self.hit_die
        }