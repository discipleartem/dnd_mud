# src/domain/entities/attribute.py
from dataclasses import dataclass, field
from typing import Optional
from ..value_objects.attributes import get_standard_attributes, StandardAttribute


@dataclass
class Attribute:
    """Атрибут персонажа с автоматической валидацией и конфигурацией."""

    name: str
    value: int = 10
    description: str = field(default="", init=False)

    def __post_init__(self) -> None:
        """Инициализация после создания dataclass."""
        self.validate()
        if not self.description:
            self.description = self._get_description()

    def _get_description(self) -> str:
        """Возвращает описание из конфигурации."""
        attr_config = self._get_config()
        return attr_config.description if attr_config else ""

    def _get_config(self) -> Optional[StandardAttribute]:
        """Возвращает конфигурацию атрибута."""
        return get_standard_attributes().get_attribute(self.name)

    @property
    def bounds(self) -> tuple[int, int]:
        """Возвращает границы значений для характеристики."""
        attr_config = self._get_config()
        if attr_config:
            return (attr_config.min_value, attr_config.max_value)
        return (3, 20)

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        attr_config = self._get_config()
        return attr_config.name if attr_config else self.name

    @property
    def is_valid(self) -> bool:
        """Проверяет валидность значения."""
        min_val, max_val = self.bounds
        return min_val <= self.value <= max_val

    def validate(self) -> None:
        """Проверяет и выбрасывает исключение если невалидно."""
        if not self.is_valid:
            min_val, max_val = self.bounds
            raise ValueError(
                f"Значение характеристики {self.name} должно быть от {min_val} до {max_val}, получено: {self.value}"
            )
