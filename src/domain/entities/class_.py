"""
Модуль классов D&D MUD.

Определяет класс персонажа и их особенности.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class CharacterClass:
    """Класс персонажа D&D."""
    
    name: str
    description: str
    hit_die: str = "d10"  # Кубик для HP
    
    # Дополнительные поля из YAML
    primary_ability: str = "strength"
    saving_throws: List[str] = field(default_factory=list)
    armor_proficiencies: List[str] = field(default_factory=list)
    weapon_proficiencies: List[str] = field(default_factory=list)
    spellcasting: Dict[str, Any] = field(default_factory=dict)
    divine_domain: Optional[str] = None
    skills: Dict[str, Any] = field(default_factory=dict)
    
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
            'hit_die': self.hit_die,
            'primary_ability': self.primary_ability,
            'saving_throws': self.saving_throws,
            'armor_proficiencies': self.armor_proficiencies,
            'weapon_proficiencies': self.weapon_proficiencies,
            'spellcasting': self.spellcasting,
            'divine_domain': self.divine_domain,
            'skills': self.skills
        }
    
    def has_spellcasting(self) -> bool:
        """Проверяет, может ли класс колдовать."""
        return bool(self.spellcasting)
    
    def get_saving_throw_modifier(self, ability: str, character: 'Character') -> int:
        """Рассчитывает модификатор спасброска.
        
        Args:
            ability: Характеристика для спасброска
            character: Объект персонажа
            
        Returns:
            Модификатор спасброска
        """
        from ..value_objects.saving_throws import SavingThrowsManager
        
        # Проверяем, существует ли спасбросок для характеристики
        if not SavingThrowsManager.is_valid_saving_throw(ability):
            return character.get_ability_modifier(getattr(character, ability).value)
        
        # Базовый модификатор характеристики
        base_modifier = character.get_ability_modifier(getattr(character, ability).value)
        
        # Если класс имеет мастерство в этом спасброске, добавляем бонус
        if ability in self.saving_throws:
            return base_modifier + 2  # Профессиональный бонус
        else:
            return base_modifier
    
    def get_save_proficiencies(self) -> List[str]:
        """Возвращает список владений спасбросками класса."""
        return self.saving_throws.copy()
    
    def get_ac_bonus(self) -> int:
        """Возвращает бонус к классу доспеха от класса."""
        # У воинов есть мастерство доспехов
        if self.name == "Воин":
            return 1
        return 0