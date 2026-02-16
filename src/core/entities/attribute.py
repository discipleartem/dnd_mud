# src/core/entities/attribute.py
from ..localization.loader import localization

@dataclass
class Attribute:
    name: str
    value: int = field(default=10, min=1, max=20)
    description: str = field(default="")
    
    def __post_init__(self) -> None:
        """Загружает локализацию."""
        info = localization.get_attribute_info(self.name)
        # НЕ меняем name - это ключ для локализации!
        self.description = info.get('description', self.description)
    
    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return localization.get_attribute_name(self.name)