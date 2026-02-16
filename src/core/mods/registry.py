# src/core/mods/registry.py
from typing import Dict, Optional
from ..mechanics.attributes import StandardAttribute

class ModRegistry:
    """Реестр модов - ТОЛЬКО расширения."""
    
    def __init__(self):
        self._custom_attributes: Dict[str, StandardAttribute] = {}
    
    def register_custom_attribute(self, attribute: StandardAttribute) -> None:
        """Регистрирует кастомную характеристику из мода."""
        self._custom_attributes[attribute.name] = attribute
    
    def get_custom_attribute(self, name: str) -> Optional[StandardAttribute]:
        """Возвращает кастомную характеристику."""
        return self._custom_attributes.get(name)
    
    def get_all_attributes(self) -> Dict[str, StandardAttribute]:
        """Возвращает стандартные + кастомные характеристики."""
        from ..mechanics.attributes import StandardAttributes
        
        all_attrs = StandardAttributes.get_all().copy()
        all_attrs.update(self._custom_attributes)
        return all_attrs

# Глобальный реестр
mod_registry = ModRegistry()