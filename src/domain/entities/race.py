"""
Модуль рас D&D MUD.

Определяет класс расы и их бонусы к характеристикам.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from ..interfaces.localization import get_text


@dataclass
class Race:
    """Класс расы D&D."""

    name: str
    bonuses: Dict[str, int] = field(default_factory=dict)
    description: str = field(default="")
    short_description: str = field(default="")
    size: str = field(default="medium")
    speed: int = field(default=30)
    age: Optional[Dict[str, int]] = field(default=None)
    languages: Optional[Dict[str, Any]] = field(default=None)
    features: List[Dict[str, Any]] = field(default_factory=list)
    subraces: Dict[str, "Race"] = field(default_factory=dict)
    inherit_bonuses: bool = field(default=True)
    inherit_features: bool = field(default=True)
    alternative_features: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Инициализация полей по умолчанию."""
        if not self.short_description and self.description:
            # Генерируем короткое описание из полного
            sentences = self.description.split('.')
            short_sentences = [s.strip() for s in sentences[:2] if s.strip()]
            self.short_description = '. '.join(short_sentences)
            if self.short_description and not self.short_description.endswith('.'):
                self.short_description += '.'
        
        # Инициализация языков
        if self.languages is None:
            self.languages = {"base": [], "choice": 0}
        
        # Инициализация возраста
        if self.age is None:
            self.age = {"min": 16, "max": 100}

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return get_text(f"race_name.{self.name}")

    def get_effective_bonuses(self, subrace_bonuses: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        """Возвращает эффективные бонусы с учетом наследования.
        
        Args:
            subrace_bonuses: Бонусы подрасы (если есть)
            
        Returns:
            Словарь с итоговыми бонусами
        """
        result = {}
        
        # Если наследуем бонусы, начинаем с базовых
        if self.inherit_bonuses:
            result.update(self.bonuses)
        
        # Добавляем бонусы подрасы
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
        """Возвращает все особенности с учетом наследования.
        
        Args:
            subrace_features: Особенности подрасы (если есть)
            
        Returns:
            Список всех особенностей
        """
        result = []
        
        # Если наследуем особенности, начинаем с базовых
        if self.inherit_features and self.features:
            result.extend(self.features)
        
        # Добавляем особенности подрасы
        if subrace_features:
            result.extend(subrace_features)
        
        return result

    def apply_bonuses(self, attributes: Dict[str, int], chosen_attributes: Optional[List[str]] = None) -> Dict[str, int]:
        """Применяет расовые бонусы к характеристикам.
        
        Args:
            attributes: Текущие значения характеристик
            chosen_attributes: Список выбранных характеристик для особенностей типа ability_choice
            
        Returns:
            Словарь с обновленными значениями характеристик
        """
        result = attributes.copy()
        
        # Применяем бонусы из поля bonuses
        for attr_name, bonus in self.bonuses.items():
            if attr_name in result:
                result[attr_name] += bonus
        
        # Обрабатываем особенности с выбором характеристик
        if chosen_attributes:
            for feature in self.features:
                if feature.get("type") == "ability_choice":
                    max_choices = feature.get("max_choices", 1)
                    bonus_value = feature.get("bonus_value", 1)
                    allowed_attributes = feature.get("allowed_attributes", list(attributes.keys()))
                    
                    # Применяем бонусы к выбранным характеристикам
                    applied_count = 0
                    for attr_name in chosen_attributes:
                        if (applied_count < max_choices and 
                            attr_name in allowed_attributes and 
                            attr_name in result):
                            result[attr_name] += bonus_value
                            applied_count += 1
                    
                    # Если выбрано меньше чем разрешено, применяем к первым разрешенным
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
        """Возвращает особенности с выбором характеристик.
        
        Returns:
            Список особенностей типа ability_choice
        """
        return [feature for feature in self.features if feature.get("type") == "ability_choice"]
    
    def has_ability_choice(self) -> bool:
        """Проверяет, есть ли у расы особенности с выбором характеристик.
        
        Returns:
            True если есть особенности типа ability_choice
        """
        return bool(self.get_ability_choice_features())
    
    def get_max_ability_choices(self) -> int:
        """Возвращает максимальное количество выборов характеристик.
        
        Returns:
            Сумма max_choices из всех особенностей ability_choice
        """
        total = 0
        for feature in self.get_ability_choice_features():
            total += feature.get("max_choices", 1)
        return total
    
    def get_allowed_attributes(self) -> List[str]:
        """Возвращает список доступных для выбора характеристик.
        
        Returns:
            Список характеристик, которые можно выбрать
        """
        allowed = set()
        for feature in self.get_ability_choice_features():
            feature_allowed = feature.get("allowed_attributes", [])
            allowed.update(feature_allowed)
        
        return list(allowed) if allowed else ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
