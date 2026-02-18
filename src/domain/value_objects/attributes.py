# src/core/mechanics/attributes.py
from dataclasses import dataclass
from typing import Dict


@dataclass
class StandardAttribute:
    """Стандартная характеристика D&D."""
    name: str
    default_value: int = 10
    min_value: int = 1
    max_value: int = 20
    short_name: str = ""
    description: str = ""


class StandardAttributes:
    """Стандартный набор характеристик D&D."""
    
    _config: Dict[str, StandardAttribute] = {
        "strength": StandardAttribute("strength", 10, 1, 20, "STR", "Сила"),
        "dexterity": StandardAttribute("dexterity", 10, 1, 20, "DEX", "Ловкость"),
        "constitution": StandardAttribute("constitution", 10, 1, 20, "CON", "Телосложение"),
        "intelligence": StandardAttribute("intelligence", 10, 1, 20, "INT", "Интеллект"),
        "wisdom": StandardAttribute("wisdom", 10, 1, 20, "WIS", "Мудрость"),
        "charisma": StandardAttribute("charisma", 10, 1, 20, "CHA", "Харизма"),
    }

    @classmethod
    def get_all(cls) -> Dict[str, StandardAttribute]:
        """Возвращает все стандартные характеристики."""
        return cls._config

    @classmethod
    def get_attribute(cls, name: str) -> StandardAttribute:
        """Возвращает атрибут по имени."""
        return cls._config.get(name)

    @classmethod
    def validate_value(cls, name: str, value: int) -> bool:
        """Проверяет значение характеристики."""
        attr = cls.get_attribute(name)
        return attr.min_value <= value <= attr.max_value if attr else False
