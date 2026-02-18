# src/core/entities/attribute.py
from dataclasses import dataclass, field
from ..value_objects.attributes import StandardAttributes


@dataclass
class Attribute:
    name: str
    value: int = 10
    description: str = ""

    def __post_init__(self) -> None:
        self.validate()
        if not self.description:
            self.description = self._get_description()

    def _get_description(self) -> str:
        """Возвращает описание из конфигурации."""
        info = StandardAttributes.get_attribute(self.name)
        return info.description if info else ""

    @property
    def bounds(self) -> tuple[int, int]:
        """Возвращает границы значений для характеристики."""
        attr_config = StandardAttributes.get_attribute(self.name)
        return (attr_config.min_value, attr_config.max_value) if attr_config else (3, 20)

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        info = StandardAttributes.get_attribute(self.name)
        return info.name if info else self.name

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
