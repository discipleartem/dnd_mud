"""Доменные сущности для характеристик и навыков D&D.

Чистые доменные сущности following принципам Clean Architecture.
Не зависят от внешних слоев.
"""

from dataclasses import dataclass
from enum import Enum


class AbilityEnum(Enum):
    """Характеристики D&D 5e."""

    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

    def get_modifier(self, value: int) -> int:
        """Получить модификатор характеристики.

        Args:
            value: Значение характеристики

        Returns:
            Модификатор характеристики
        """
        return (value - 10) // 2

    @classmethod
    def get_all_abilities(cls) -> list["AbilityEnum"]:
        """Получить все характеристики.

        Returns:
            Список всех характеристик
        """
        return list(cls)

    def get_localized_key(self) -> str:
        """Получить ключ для локализации.

        Returns:
            Ключ для перевода
        """
        return f"abilities.{self.value}"


@dataclass(frozen=True)
class Ability:
    """Характеристика персонажа."""

    name: str
    description: str = ""
    abbreviation: str = ""

    def __str__(self) -> str:
        """Строковое представление."""
        return self.name

    def get_abbreviation(self) -> str:
        """Получить сокращение.

        Returns:
            Сокращение характеристики
        """
        return self.abbreviation or self.name[:3].upper()


@dataclass(frozen=True)
class Skill:
    """Навык персонажа."""

    name: str
    description: str = ""
    ability: AbilityEnum = AbilityEnum.INTELLIGENCE
    requires_training: bool = True

    def __str__(self) -> str:
        """Строковое представление."""
        return self.name

    def get_modifier(self, ability_score: int) -> int:
        """Получить модификатор навыка.

        Args:
            ability_score: Значение связанной характеристики

        Returns:
            Модификатор навыка
        """
        base_modifier = self.ability.get_modifier(ability_score)
        return base_modifier + (0 if not self.requires_training else 0)

    def get_full_name(self) -> str:
        """Получить полное название с характеристикой.

        Returns:
            Полное название навыка
        """
        return f"{self.name} ({self.ability.value.title()})"


@dataclass(frozen=True)
class SkillProficiency:
    """Владение навыком."""

    skill: Skill
    proficiency_level: int = 0  # 0: нет, 1: владение, 2: экспертиза

    def is_proficient(self) -> bool:
        """Проверить наличие владения.

        Returns:
            True если есть владение
        """
        return self.proficiency_level > 0

    def is_expert(self) -> bool:
        """Проверить наличие экспертизы.

        Returns:
            True если есть экспертиза
        """
        return self.proficiency_level >= 2

    def get_bonus(self, ability_score: int, proficiency_bonus: int) -> int:
        """Получить бонус навыка.

        Args:
            ability_score: Значение характеристики
            proficiency_bonus: Бонус владения

        Returns:
            Общий бонус навыка
        """
        base_modifier = self.skill.get_modifier(ability_score)

        if not self.is_proficient():
            return base_modifier

        proficiency_multiplier = 1 if self.is_proficient() else 0
        if self.is_expert():
            proficiency_multiplier = 2

        return base_modifier + (proficiency_bonus * proficiency_multiplier)


class SkillFactory:
    """Фабрика для создания навыков."""

    # Стандартные навыки D&D 5e
    STANDARD_SKILLS = {
        "athletics": Skill("Athletics", "Атлетика", AbilityEnum.STRENGTH),
        "acrobatics": Skill("Acrobatics", "Акробатика", AbilityEnum.DEXTERITY),
        "sleight_of_hand": Skill(
            "Sleight of Hand", "Ловкость рук", AbilityEnum.DEXTERITY
        ),
        "stealth": Skill("Stealth", "Скрытность", AbilityEnum.DEXTERITY),
        "arcana": Skill("Arcana", "Магия", AbilityEnum.INTELLIGENCE),
        "history": Skill("History", "История", AbilityEnum.INTELLIGENCE),
        "investigation": Skill(
            "Investigation", "Расследование", AbilityEnum.INTELLIGENCE
        ),
        "nature": Skill("Nature", "Природа", AbilityEnum.INTELLIGENCE),
        "religion": Skill("Religion", "Религия", AbilityEnum.INTELLIGENCE),
        "animal_handling": Skill(
            "Animal Handling", "Обращение с животными", AbilityEnum.WISDOM
        ),
        "insight": Skill("Insight", "Проницательность", AbilityEnum.WISDOM),
        "medicine": Skill("Medicine", "Медицина", AbilityEnum.WISDOM),
        "perception": Skill("Perception", "Восприятие", AbilityEnum.WISDOM),
        "survival": Skill("Survival", "Выживание", AbilityEnum.WISDOM),
        "deception": Skill("Deception", "Обман", AbilityEnum.CHARISMA),
        "intimidation": Skill(
            "Intimidation", "Запугивание", AbilityEnum.CHARISMA
        ),
        "performance": Skill(
            "Performance", "Исполнение", AbilityEnum.CHARISMA
        ),
        "persuasion": Skill("Persuasion", "Убеждение", AbilityEnum.CHARISMA),
    }

    @classmethod
    def create_skill(cls, skill_id: str) -> Skill:
        """Создать навык по ID.

        Args:
            skill_id: ID навыка

        Returns:
            Объект навыка

        Raises:
            ValueError: Если навык не найден
        """
        if skill_id not in cls.STANDARD_SKILLS:
            raise ValueError(f"Неизвестный навык: {skill_id}")

        return cls.STANDARD_SKILLS[skill_id]

    @classmethod
    def get_all_skills(cls) -> list[Skill]:
        """Получить все стандартные навыки.

        Returns:
            Список всех навыков
        """
        return list(cls.STANDARD_SKILLS.values())

    @classmethod
    def get_skills_by_ability(cls, ability: AbilityEnum) -> list[Skill]:
        """Получить навыки для характеристики.

        Args:
            ability: Характеристика

        Returns:
            Список навыков использующих эту характеристику
        """
        return [
            skill
            for skill in cls.STANDARD_SKILLS.values()
            if skill.ability == ability
        ]
