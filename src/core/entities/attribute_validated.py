# src/core/entities/attribute_validated.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from ..localization.loader import localization


@dataclass
class AttributeConfig:
    """Конфигурация атрибута из YAML."""
    name: str
    default_value: int = 10
    min_value: int = 0  # Будет переопределено из конфига
    max_value: int = 0  # Будет переопределено из конфига
    short_name: str = ""
    description: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttributeConfig':
        """Создает конфигурацию из словаря."""
        return cls(
            name=data.get('name', ''),
            default_value=data.get('default_value', 10),
            min_value=data.get('min_value', 1),
            max_value=data.get('max_value', 20),
            short_name=data.get('short_name', ''),
            description=data.get('description', '')
        )


@dataclass
class ValidatedAttribute:
    """Атрибут с валидацией на основе конфигурации."""
    name: str
    value: int = 10
    description: str = ""
    _config: Optional[AttributeConfig] = field(default=None, init=False)
    
    def __post_init__(self) -> None:
        """Загружает конфигурацию и локализацию."""
        self._load_config()
        self._load_localization()
        self._validate()
    
    def _load_config(self) -> None:
        """Загружает конфигурацию атрибута."""
        attributes_config = localization.get_core_attributes()
        attr_data = attributes_config.get('base_attributes', {}).get(self.name, {})
        
        if attr_data:
            self._config = AttributeConfig.from_dict(attr_data)
            # Устанавливаем значение по умолчанию если не задано
            if self.value == 10:  # значение по умолчанию в dataclass
                self.value = self._config.default_value
        else:
            # Fallback конфигурация если атрибут не найден
            self._config = AttributeConfig(name=self.name)
    
    def _load_localization(self) -> None:
        """Загружает локализацию."""
        info = localization.get_attribute_info(self.name)
        if not self.description:
            self.description = info.get('description', self.description)
    
    def _validate(self) -> None:
        """Проверяет значение атрибута."""
        if not self._config:
            raise ValueError(f"Конфигурация для атрибута '{self.name}' не найдена")
        
        if not (self._config.min_value <= self.value <= self._config.max_value):
            raise ValueError(
                f"Значение характеристики '{self.name}' должно быть от "
                f"{self._config.min_value} до {self._config.max_value}, получено: {self.value}"
            )
    
    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return localization.get_attribute_name(self.name)
    
    @property
    def short_name(self) -> str:
        """Возвращает короткое название."""
        return self._config.short_name if self._config else ""
    
    @property
    def min_value(self) -> int:
        """Возвращает минимальное допустимое значение."""
        return self._config.min_value if self._config else 3
    
    @property
    def max_value(self) -> int:
        """Возвращает максимальное допустимое значение."""
        return self._config.max_value if self._config else 18
    
    @property
    def is_valid(self) -> bool:
        """Проверяет валидность значения."""
        if not self._config:
            return False
        return self._config.min_value <= self.value <= self._config.max_value
    
    def validate(self) -> None:
        """Проверяет и выбрасывает исключение если невалидно."""
        self._validate()
    
    def set_value(self, new_value: int) -> None:
        """Устанавливает новое значение с валидацией."""
        old_value = self.value
        self.value = new_value
        try:
            self._validate()
        except ValueError as e:
            # Возвращаем старое значение при ошибке валидации
            self.value = old_value
            raise e
    
    def apply_bonus(self, bonus: int) -> None:
        """Применяет бонус к значению с валидацией."""
        self.set_value(self.value + bonus)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует в словарь."""
        return {
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'short_name': self.short_name
        }


# Пример использования:
if __name__ == "__main__":
    try:
        # Создаем атрибут с валидацией
        strength = ValidatedAttribute(name="strength", value=16)
        print(f"Создан атрибут: {strength.localized_name} = {strength.value}")
        print(f"Диапазон: {strength.min_value}-{strength.max_value}")
        print(f"Короткое имя: {strength.short_name}")
        
        # Пробуем установить невалидное значение
        try:
            strength.set_value(25)
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        
        # Применяем бонус
        strength.apply_bonus(2)
        print(f"После бонуса +2: {strength.value}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
