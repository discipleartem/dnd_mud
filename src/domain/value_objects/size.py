"""Value Object для размера персонажа.

Представляет размер в D&D с поддержкой локализации и сравнения.
Следует принципу неизменяемости Value Objects.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional


class SizeCategory(Enum):
    """Категории размеров D&D."""

    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"
    COLOSSAL = "colossal"


@dataclass(frozen=True)
class Size:
    """Размер персонажа или существа.

    Value Object - неизменяемый объект, определяемый своими атрибутами.
    """

    category: SizeCategory
    space_in_feet: int  # Пространство которое занимает (в футах)
    reach_in_feet: int  # Достижимость (в футах)

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        if self.space_in_feet <= 0:
            raise ValueError("Пространство должно быть положительным числом")

        if self.reach_in_feet <= 0:
            raise ValueError("Достижимость должна быть положительным числом")

    @classmethod
    def from_category(cls, category: SizeCategory) -> "Size":
        """Создать размер из категории с параметрами по умолчанию.

        Args:
            category: Категория размера

        Returns:
            Объект Size с параметрами по умолчанию для категории
        """
        default_params = {
            SizeCategory.TINY: (2, 0),  # Округляем до целых
            SizeCategory.SMALL: (5, 5),
            SizeCategory.MEDIUM: (5, 5),
            SizeCategory.LARGE: (10, 10),
            SizeCategory.HUGE: (15, 15),
            SizeCategory.GARGANTUAN: (20, 20),
            SizeCategory.COLOSSAL: (30, 30),
        }

        space, reach = default_params[category]
        return cls(category=category, space_in_feet=space, reach_in_feet=reach)

    def get_localized_name(
        self, localization_service: Optional["ILocalizationService"] = None
    ) -> str:
        """Получить локализованное название размера.

        Args:
            localization_service: Сервис локализации (опционально)

        Returns:
            Локализованное название или ключ если сервис не предоставлен
        """
        if localization_service:
            return localization_service.translate(
                f"character.size.{self.category.value}"
            )

        # Fallback - возвращаем ключ если нет сервиса локализации
        return self.category.value

    def is_larger_than(self, other: "Size") -> bool:
        """Проверить, что этот размер больше другого.

        Args:
            other: Другой размер для сравнения

        Returns:
            True если этот размер больше
        """
        size_order = [
            SizeCategory.TINY,
            SizeCategory.SMALL,
            SizeCategory.MEDIUM,
            SizeCategory.LARGE,
            SizeCategory.HUGE,
            SizeCategory.GARGANTUAN,
            SizeCategory.COLOSSAL,
        ]

        return size_order.index(self.category) > size_order.index(
            other.category
        )

    def is_smaller_than(self, other: "Size") -> bool:
        """Проверить, что этот размер меньше другого.

        Args:
            other: Другой размер для сравнения

        Returns:
            True если этот размер меньше
        """
        return other.is_larger_than(self)

    def get_modifier_for_stealth(self) -> int:
        """Получить модификатор для проверки Скрытности.

        Returns:
            Модификатор к проверке Скрытности
        """
        stealth_modifiers = {
            SizeCategory.TINY: 2,
            SizeCategory.SMALL: 1,
            SizeCategory.MEDIUM: 0,
            SizeCategory.LARGE: -1,
            SizeCategory.HUGE: -2,
            SizeCategory.GARGANTUAN: -2,
            SizeCategory.COLOSSAL: -4,
        }

        return stealth_modifiers[self.category]

    def __str__(self) -> str:
        """Строковое представление."""
        return f"Size({self.category.value})"

    def __repr__(self) -> str:
        """Детальное строковое представление."""
        return f"Size(category={self.category.value}, space={self.space_in_feet}ft, reach={self.reach_in_feet}ft)"


# Импорт для аннотации
if TYPE_CHECKING:
    from src.interfaces.services import ILocalizationService
