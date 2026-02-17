# src/core/entities/skill.py
from dataclasses import dataclass, field
from ..interfaces.localization import get_text
from ..value_objects.skills import SkillsManager


@dataclass
class Skill:
    """Класс навыка D&D."""

    name: str  # "athletics", "stealth", etc.
    proficiency_bonus: int = field(default=0)  # Бонус мастерства (0, +2, +3, etc.)
    expertise_bonus: int = field(default=0)  # Бонус экспертизы (двойной мастерство)
    custom_bonus: int = field(
        default=0
    )  # Дополнительные бонусы от предметов/заклинаний

    def __post_init__(self) -> None:
        """Валидация и загрузка локализации."""
        skill_config = SkillsManager.get_skill(self.name)
        if not skill_config:
            raise ValueError(f"Неизвестный навык: {self.name}")

        # Валидация бонусов
        if self.proficiency_bonus < 0:
            raise ValueError(
                f"Бонус мастерства не может быть отрицательным: {self.proficiency_bonus}"
            )

        if self.expertise_bonus < 0:
            raise ValueError(
                f"Бонус экспертизы не может быть отрицательным: {self.expertise_bonus}"
            )

    @property
    def config(self):
        """Возвращает конфигурацию навыка."""
        return SkillsManager.get_skill(self.name)

    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название навыка."""
        return get_text(f"skill_name.{self.name}")

    @property
    def localized_description(self) -> str:
        """Возвращает локализованное описание."""
        return get_text(f"skill_description.{self.name}")

    @property
    def attribute_name(self) -> str:
        """Возвращает название связанной характеристики."""
        return self.config.attribute if self.config else "strength"

    @property
    def is_proficient(self) -> bool:
        """Проверяет, обладает ли персонаж мастерством в навыке."""
        return self.proficiency_bonus > 0

    @property
    def has_expertise(self) -> bool:
        """Проверяет, обладает ли персонаж экспертизой в навыке."""
        return self.expertise_bonus > 0

    def calculate_total_bonus(
        self, character_attributes: dict, proficiency_bonus: int, penalties: dict = None
    ) -> int:
        """Рассчитывает общий бонус навыка с учётом штрафов.

        Args:
            character_attributes: Словарь со значениями характеристик персонажа
            proficiency_bonus: Бонус мастерства персонажа
            penalties: Словарь штрафов (например {"armor": -2})

        Returns:
            Общий бонус к навыку
        """
        # Модификатор характеристики
        attribute_value = character_attributes.get(self.attribute_name, 10)
        attribute_modifier = (attribute_value - 10) // 2

        # Бонус мастерства
        proficiency = self.proficiency_bonus if self.proficiency_bonus > 0 else 0

        # Бонус экспертизы
        expertise = self.expertise_bonus if self.expertise_bonus > 0 else 0

        # Общий бонус
        total_bonus = attribute_modifier + proficiency + expertise + self.custom_bonus

        # Применяем штрафы
        if penalties:
            skill_penalties = SkillsManager.get_penalties(self.name)
            for penalty_type in skill_penalties:
                if penalty_type in penalties:
                    total_bonus += penalties[penalty_type]

        return total_bonus

    def add_proficiency(self, bonus: int = 2) -> None:
        """Добавляет мастерство в навык.

        Args:
            bonus: Величина бонуса мастерства (обычно +2)
        """
        if bonus < 0:
            raise ValueError("Бонус мастерства не может быть отрицательным")
        self.proficiency_bonus = bonus

    def add_expertise(self, bonus: int = 4) -> None:
        """Добавляет экспертизу в навык.

        Args:
            bonus: Величина бонуса экспертизы (обычно +4, двойной мастерство)
        """
        if bonus < 0:
            raise ValueError("Бонус экспертизы не может быть отрицательным")
        self.expertise_bonus = bonus

    def add_custom_bonus(self, bonus: int) -> None:
        """Добавляет пользовательский бонус.

        Args:
            bonus: Величина дополнительного бонуса
        """
        self.custom_bonus += bonus

    def remove_proficiency(self) -> None:
        """Удаляет мастерство из навыка."""
        self.proficiency_bonus = 0

    def remove_expertise(self) -> None:
        """Удаляет экспертизу из навыка."""
        self.expertise_bonus = 0

    def has_penalty(self, penalty_type: str) -> bool:
        """Проверяет, применяется ли к навыку указанный штраф."""
        return SkillsManager.has_penalty(self.name, penalty_type)

    def get_penalties(self) -> list:
        """Возвращает список штрафов для навыка."""
        return SkillsManager.get_penalties(self.name)

    def reset_custom_bonus(self) -> None:
        """Сбрасывает пользовательский бонус."""
        self.custom_bonus = 0

    def __str__(self) -> str:
        """Строковое представление навыка."""
        status = []
        if self.is_proficient:
            status.append("мастерство")
        if self.has_expertise:
            status.append("экспертиза")

        status_str = f" ({', '.join(status)})" if status else ""
        return f"{self.localized_name}{status_str}"

    def __repr__(self) -> str:
        """Полное строковое представление."""
        return (
            f"Skill(name='{self.name}', proficiency_bonus={self.proficiency_bonus}, "
            f"expertise_bonus={self.expertise_bonus}, custom_bonus={self.custom_bonus})"
        )
