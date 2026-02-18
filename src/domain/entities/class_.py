"""
Модуль классов D&D MUD.

Определяет класс персонажа и их особенности.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import re


@dataclass
class CharacterClass:
    """Класс персонажа D&D."""
    
    name: str
    description: str
    hit_die: str = "d10"
    primary_ability: str = "strength"
    saving_throws: List[str] = None
    armor_proficiencies: List[str] = None
    weapon_proficiencies: List[str] = None
    spellcasting: Dict[str, Any] = None
    divine_domain: Optional[str] = None
    skills: Dict[str, Any] = None

    def __post_init__(self) -> None:
        self.saving_throws = self.saving_throws or []
        self.armor_proficiencies = self.armor_proficiencies or []
        self.weapon_proficiencies = self.weapon_proficiencies or []
        self.spellcasting = self.spellcasting or {}
        self.skills = self.skills or {}

    def calculate_hp(self, constitution: int) -> int:
        """Рассчитывает максимальное HP."""
        match = re.search(r"d(\d+)", self.hit_die)
        if match:
            hit_die_value = int(match.group(1))
            con_modifier = (constitution - 10) // 2
            return hit_die_value + con_modifier
        return 10 + (constitution - 10) // 2

    def has_spellcasting(self) -> bool:
        """Проверяет, может ли класс колдовать."""
        return bool(self.spellcasting)

    def get_save_proficiencies(self) -> List[str]:
        """Возвращает список владений спасбросками класса."""
        return self.saving_throws.copy()

    def get_ac_bonus(self) -> int:
        """Возвращает бонус к классу доспеха от класса."""
        return 1 if self.name == "Воин" else 0
