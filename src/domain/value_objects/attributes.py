# src/domain/value_objects/attributes.py
"""Стандартные атрибуты D&D 5e."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..interfaces.localization import get_text


@dataclass
class StandardAttribute:
    """Стандартный атрибут характеристики."""

    name: str
    default_value: int = 10
    min_value: int = 1
    max_value: int = 20
    short_name: str = field(default="", init=False)
    description: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if not self.short_name:
            self.short_name = self.name.upper()[:3]
        if not self.description:
            self.description = get_text(f"attribute_description.{self.name}")


@dataclass
class StandardAttributes:
    """Менеджер стандартных атрибутов."""

    _attributes: Dict[str, StandardAttribute] = field(default_factory=dict, init=False)
    _loaded: bool = field(default=False, init=False)

    def _load_attributes(self) -> None:
        """Загружает стандартные атрибуты."""
        if self._loaded:
            return

        # Встроенные атрибуты D&D 5e
        attributes_data = {
            "strength": {
                "short_name": "СИЛ",
                "description": "Физическая сила, мощь и мышечная масса",
            },
            "dexterity": {
                "short_name": "ЛОВ",
                "description": "Ловкость, рефлексы и баланс",
            },
            "constitution": {
                "short_name": "ТЕЛ",
                "description": "Выносливость, здоровье и выносливость",
            },
            "intelligence": {
                "short_name": "ИНТ",
                "description": "Интеллект, память и рассуждение",
            },
            "wisdom": {
                "short_name": "МДР",
                "description": "Мудрость, интуиция и восприятие",
            },
            "charisma": {
                "short_name": "ХАР",
                "description": "Харизма, уверенность и лидерство",
            },
        }

        self._attributes = {}
        for name, data in attributes_data.items():
            attr = StandardAttribute(name=name)
            attr.short_name = data["short_name"]
            attr.description = data["description"]
            self._attributes[name] = attr

        self._loaded = True

    def get_attribute(self, name: str) -> Optional[StandardAttribute]:
        """Возвращает атрибут по имени."""
        self._load_attributes()
        return self._attributes.get(name)

    def get_all_attributes(self) -> Dict[str, StandardAttribute]:
        """Возвращает все атрибуты."""
        self._load_attributes()
        return self._attributes.copy()

    def get_attribute_names(self) -> List[str]:
        """Возвращает все имена атрибутов."""
        self._load_attributes()
        return list(self._attributes.keys())

    def is_valid_attribute(self, name: str) -> bool:
        """Проверяет, существует ли атрибут."""
        self._load_attributes()
        return name in self._attributes


# Глобальный экземпляр для использования
_standard_attributes = StandardAttributes()


def get_standard_attributes() -> StandardAttributes:
    """Возвращает глобальный экземпляр стандартных атрибутов."""
    return _standard_attributes
