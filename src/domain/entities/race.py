"""
Модуль рас D&D MUD.

Определяет класс расы и их бонусы к характеристикам.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from ..interfaces.localization import get_text


@dataclass
class Race:
    """Класс расы D&D."""
    
    name: str
    bonuses: Dict[str, int] = None
    description: str = ""
    short_description: str = ""
    size: str = "medium"
    speed: int = 30
    age: Dict[str, int] = None
    languages: Dict[str, Any] = None
    features: List[Dict[str, Any]] = None
    subraces: Dict[str, "Race"] = None
    inherit_bonuses: bool = True
    inherit_features: bool = True
    alternative_features: Dict[str, Any] = None

    def __post_init__(self) -> None:
        self.bonuses = self.bonuses or {}
        self.features = self.features or []
        self.subraces = self.subraces or {}
        self.alternative_features = self.alternative_features or {}
        
        if not self.short_description and self.description:
            sentences = self.description.split('.')
            short_sentences = [s.strip() for s in sentences[:2] if s.strip()]
            self.short_description = '. '.join(short_sentences)
            if self.short_description and not self.short_description.endswith('.'):
                self.short_description += '.'
        
        self.languages = self.languages or {"base": [], "choice": 0}
        self.age = self.age or {"min": 16, "max": 100}

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return get_text(f"race_name.{self.name}")

    def get_effective_bonuses(self, subrace_bonuses: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        """Возвращает эффективные бонусы с учетом наследования."""
        result = {}
        
        if self.inherit_bonuses:
            result.update(self.bonuses)
        
        if subrace_bonuses:
            result.update(subrace_bonuses)
        
        return result

    def get_subrace(self, subrace_name: str) -> "Race":
        """Возвращает подрасу по имени."""
        return self.subraces.get(subrace_name)

    def add_subrace(self, subrace: "Race") -> None:
        """Добавляет подрасу."""
        self.subraces[subrace.name] = subrace

    def has_alternative_features(self) -> bool:
        """Проверяет наличие альтернативных особенностей."""
        return bool(self.alternative_features)

    def get_alternative_options(self) -> Dict[str, Any]:
        """Возвращает доступные альтернативные опции."""
        return self.alternative_features.get("options", {})

    def get_all_features(self, subrace_features: Optional[List[Dict]] = None) -> List[Dict]:
        """Возвращает все особенности с учетом наследования."""
        result = []
        
        if self.inherit_features and self.features:
            result.extend(self.features)
        
        if subrace_features:
            result.extend(subrace_features)
        
        return result

    def apply_bonuses(self, attributes: Dict[str, int], chosen_attributes: Optional[List[str]] = None) -> Dict[str, int]:
        """Применяет расовые бонусы к характеристикам."""
        result = attributes.copy()
        
        for attr_name, bonus in self.bonuses.items():
            if attr_name in result:
                result[attr_name] += bonus
        
        if chosen_attributes:
            for feature in self.features:
                if feature.get("type") == "ability_choice":
                    max_choices = feature.get("max_choices", 1)
                    bonus_value = feature.get("bonus_value", 1)
                    allowed_attributes = feature.get("allowed_attributes", list(attributes.keys()))
                    
                    applied_count = 0
                    for attr_name in chosen_attributes:
                        if (applied_count < max_choices and 
                            attr_name in allowed_attributes and 
                            attr_name in result):
                            result[attr_name] += bonus_value
                            applied_count += 1
                    
                    if applied_count < max_choices:
                        remaining = max_choices - applied_count
                        for attr_name in allowed_attributes:
                            if remaining <= 0:
                                break
                            if attr_name in result:
                                result[attr_name] += bonus_value
                                remaining -= 1
        
        return result

    def get_ability_choice_features(self) -> List[Dict[str, Any]]:
        """Возвращает особенности с выбором характеристик."""
        return [feature for feature in self.features if feature.get("type") == "ability_choice"]
    
    def has_ability_choice(self) -> bool:
        """Проверяет, есть ли у расы особенности с выбором характеристик."""
        return bool(self.get_ability_choice_features())
    
    def get_max_ability_choices(self) -> int:
        """Возвращает максимальное количество выборов характеристик."""
        return sum(feature.get("max_choices", 1) for feature in self.get_ability_choice_features())
    
    def get_allowed_attributes(self) -> List[str]:
        """Возвращает список доступных для выбора характеристик."""
        allowed = set()
        for feature in self.get_ability_choice_features():
            allowed.update(feature.get("allowed_attributes", []))
        
        return list(allowed) or ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
