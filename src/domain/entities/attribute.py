# src/core/entities/attribute.py
from dataclasses import dataclass, field
from ..interfaces.localization import get_text
from ..value_objects.attributes import StandardAttributes

@dataclass
class Attribute:
    name: str
    value: int = field(default=10)
    description: str = field(default="")
    
    def __post_init__(self) -> None:
        """Валидация и загрузка локализации."""
        # Валидация через конфигурацию
        attr_config = StandardAttributes.get_attribute(self.name)
        if attr_config:
            min_val = attr_config.min_value
            max_val = attr_config.max_value
        else:
            # Fallback значения если конфиг не найден
            min_val, max_val = 3, 20
        
        if not (min_val <= self.value <= max_val):
            raise ValueError(f"Значение характеристики {self.name} должно быть от {min_val} до {max_val}, получено: {self.value}")
        
        # Загружаем локализацию
        info = StandardAttributes.get_attribute(self.name)
        self.description = info.description
    
    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return StandardAttributes.get_attribute(self.name).name
    
    @property
    def is_valid(self) -> bool:
        """Проверяет валидность значения через конфигурацию."""
        attr_config = StandardAttributes.get_attribute(self.name)
        if attr_config:
            min_val = attr_config.min_value
            max_val = attr_config.max_value
        else:
            min_val, max_val = 3, 20
        
        return min_val <= self.value <= max_val
    
    def validate(self) -> None:
        """Проверяет и выбрасывает исключение если невалидно."""
        if not self.is_valid:
            attr_config = StandardAttributes.get_attribute(self.name)
            if attr_config:
                min_val = attr_config.min_value
                max_val = attr_config.max_value
            else:
                min_val, max_val = 3, 20
            raise ValueError(f"Значение характеристики {self.name} должно быть от {min_val} до {max_val}, получено: {self.value}")