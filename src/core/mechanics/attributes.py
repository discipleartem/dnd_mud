# src/core/mechanics/attributes.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class StandardAttribute:
    """Стандартная характеристика D&D."""
    name: str           # "strength"
    default_value: int  # 10
    min_value: int      # 1
    max_value: int      # 20
    short_name: str     # "STR"


class StandardAttributes:
    """Стандартный набор характеристик D&D."""
    
    STRENGTH = StandardAttribute("strength", 10, 1, 20, "STR")
    DEXTERITY = StandardAttribute("dexterity", 10, 1, 20, "DEX")
    CONSTITUTION = StandardAttribute("constitution", 10, 1, 20, "CON")
    INTELLIGENCE = StandardAttribute("intelligence", 10, 1, 20, "INT")
    WISDOM = StandardAttribute("wisdom", 10, 1, 20, "WIS")
    CHARISMA = StandardAttribute("charisma", 10, 1, 20, "CHA")
    
    @classmethod
    def get_all(cls) -> Dict[str, StandardAttribute]:
        """Возвращает все стандартные характеристики."""
        return {
            'strength': cls.STRENGTH,
            'dexterity': cls.DEXTERITY,
            'constitution': cls.CONSTITUTION,
            'intelligence': cls.INTELLIGENCE,
            'wisdom': cls.WISDOM,
            'charisma': cls.CHARISMA,
        }