# src/core/entities/saving_throw.py
from dataclasses import dataclass, field
from typing import Optional
from ..interfaces.localization import get_text
from ..value_objects.saving_throws import SavingThrowsManager, SavingThrowConfig


@dataclass
class SavingThrow:
    """Класс спасброска D&D."""

    name: str  # "strength_save", "dexterity_save", etc.
    proficiency_bonus: int = field(default=0)  # Бонус мастерства (0, +2, +3, etc.)
    custom_bonus: int = field(
        default=0
    )  # Дополнительные бонусы от предметов/заклинаний

    def __post_init__(self) -> None:
        """Валидация и загрузка локализации."""
        save_config = SavingThrowsManager.get_saving_throw(self.name)
        if not save_config:
            raise ValueError(f"Неизвестный спасбросок: {self.name}")

        # Валидация бонусов
        if self.proficiency_bonus < 0:
            raise ValueError(
                f"Бонус мастерства не может быть отрицательным: {self.proficiency_bonus}"
            )

    @property
    def config(self) -> Optional["SavingThrowConfig"]:
        """Возвращает конфигурацию спасброска."""
        return SavingThrowsManager.get_saving_throw(self.name)

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название спасброска."""
        return get_text(f"saving_throw_name.{self.name}")

    @property
    def localized_description(self) -> str:
        """Возвращает локализованное описание."""
        return get_text(f"saving_throw_description.{self.name}")

    @property
    def attribute_name(self) -> str:
        """Возвращает название связанной характеристики."""
        return self.config.attribute if self.config else "strength"

    @property
    def is_proficient(self) -> bool:
        """Проверяет, обладает ли персонаж мастерством в спасброске."""
        return self.proficiency_bonus > 0

    def calculate_total_bonus(
        self, character_attributes: dict[str, int], proficiency_bonus: int
    ) -> int:
        """Рассчитывает общий бонус спасброска.

        Args:
            character_attributes: Словарь со значениями характеристик персонажа
            proficiency_bonus: Бонус мастерства персонажа

        Returns:
            Общий бонус к спасброску
        """
        # Модификатор характеристики
        attribute_value = character_attributes.get(self.attribute_name, 10)
        attribute_modifier = (attribute_value - 10) // 2

        # Бонус мастерства (если персонаж имеет мастерство в спасброске)
        proficiency = self.proficiency_bonus if self.proficiency_bonus > 0 else 0

        # Общий бонус
        total_bonus = attribute_modifier + proficiency + self.custom_bonus

        return total_bonus

    def add_proficiency(self, bonus: int = 2) -> None:
        """Добавляет мастерство в спасбросок.

        Args:
            bonus: Величина бонуса мастерства (обычно +2)
        """
        if bonus < 0:
            raise ValueError("Бонус мастерства не может быть отрицательным")
        self.proficiency_bonus = bonus

    def add_custom_bonus(self, bonus: int) -> None:
        """Добавляет пользовательский бонус.

        Args:
            bonus: Величина дополнительного бонуса
        """
        self.custom_bonus += bonus

    def remove_proficiency(self) -> None:
        """Удаляет мастерство из спасброска."""
        self.proficiency_bonus = 0

    def reset_custom_bonus(self) -> None:
        """Сбрасывает пользовательский бонус."""
        self.custom_bonus = 0

    def __str__(self) -> str:
        """Строковое представление спасброска."""
        status = " (мастерство)" if self.is_proficient else ""
        return f"{self.localized_name}{status}"

    def __repr__(self) -> str:
        """Полное строковое представление."""
        return (
            f"SavingThrow(name='{self.name}', proficiency_bonus={self.proficiency_bonus}, "
            f"custom_bonus={self.custom_bonus})"
        )
