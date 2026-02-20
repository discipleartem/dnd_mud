# src/domain/services/level_resolver.py
"""Сервис для работы с уровнями персонажей."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class LevelInfo:
    """Информация об уровне."""

    level: int
    proficiency_bonus: int
    features: List[str]
    spell_slots: dict[str, List[int]] = field(default_factory=dict)


class LevelResolver:
    """Резолвер уровней D&D 5e."""

    # Бонус мастерства по уровням
    PROFICIENCY_BONUSES = {
        1: 2,
        2: 2,
        3: 2,
        4: 2,
        5: 3,
        6: 3,
        7: 3,
        8: 3,
        9: 4,
        10: 4,
        11: 4,
        12: 4,
        13: 5,
        14: 5,
        15: 5,
        16: 5,
        17: 6,
        18: 6,
        19: 6,
        20: 6,
    }

    # Опыт для уровлений
    EXPERIENCE_TABLE = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000,
        11: 85000,
        12: 100000,
        13: 120000,
        14: 140000,
        15: 165000,
        16: 195000,
        17: 225000,
        18: 265000,
        19: 305000,
        20: 355000,
    }

    @classmethod
    def get_proficiency_bonus(cls, level: int) -> int:
        """Возвращает бонус мастерства для уровня."""
        if level < 1 or level > 20:
            raise ValueError(f"Уровень должен быть от 1 до 20, получено: {level}")
        return cls.PROFICIENCY_BONUSES[level]

    @classmethod
    def get_experience_for_level(cls, level: int) -> int:
        """Возвращает опыт для достижения уровня."""
        if level < 1 or level > 20:
            raise ValueError(f"Уровень должен быть от 1 до 20, получено: {level}")
        return cls.EXPERIENCE_TABLE[level]

    @classmethod
    def get_level_by_experience(cls, experience: int) -> int:
        """Возвращает уровень по количеству опыта."""
        for level, required_exp in reversed(cls.EXPERIENCE_TABLE.items()):
            if experience >= required_exp:
                return level
        return 1

    @classmethod
    def get_experience_to_next_level(cls, current_level: int) -> int:
        """Возвращает опыт до следующего уровня."""
        if current_level >= 20:
            return 0  # Максимальный уровень

        current_exp = cls.EXPERIENCE_TABLE[current_level]
        next_exp = cls.EXPERIENCE_TABLE[current_level + 1]
        return next_exp - current_exp

    @classmethod
    def can_level_up(cls, current_level: int, experience: int) -> bool:
        """Проверяет, может ли персонаж повысить уровень."""
        if current_level >= 20:
            return False

        required_exp = cls.EXPERIENCE_TABLE[current_level + 1]
        return experience >= required_exp

    @classmethod
    def get_level_info(cls, level: int) -> LevelInfo:
        """Возвращает полную информацию об уровне."""
        if level < 1 or level > 20:
            raise ValueError(f"Уровень должен быть от 1 до 20, получено: {level}")

        return LevelInfo(
            level=level,
            proficiency_bonus=cls.PROFICIENCY_BONUSES[level],
            features=cls._get_level_features(level),
            spell_slots=cls._get_spell_slots(level),
        )

    @classmethod
    def _get_level_features(cls, level: int) -> List[str]:
        """Возвращает особенности уровня (базовая реализация)."""
        # Здесь можно добавить особенности для разных классов
        features = []

        # Общие особенности для всех классов
        if level == 1:
            features.extend(["Базовые атаки", " Владение оружием/броней"])
        if level == 4:
            features.append("Увеличение характеристики")
        if level == 8:
            features.append("Увеличение характеристики")
        if level == 12:
            features.append("Увеличение характеристики")
        if level == 16:
            features.append("Увеличение характеристики")
        if level == 19:
            features.append("Увеличение характеристики")

        return features

    @classmethod
    def _get_spell_slots(cls, level: int) -> Dict[str, List[int]]:
        """Возвращает слоты заклинаний для уровня (базовая реализация)."""
        # Это упрощенная версия. В реальности зависит от класса
        if level <= 4:
            return {}
        return {
            "level_1": [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4][
                :level
            ],
            "level_2": [2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3][
                : max(0, level - 1)
            ],
            "level_3": [0, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3][
                : max(0, level - 2)
            ],
        }

    @classmethod
    def get_valid_levels(cls) -> List[int]:
        """Возвращает список допустимых уровней."""
        return list(range(1, 21))

    @classmethod
    def is_valid_level(cls, level: int) -> bool:
        """Проверяет, допустимый ли уровень."""
        return 1 <= level <= 20

    @classmethod
    def get_level_range(cls) -> Tuple[int, int]:
        """Возвращает диапазон уровней."""
        return (1, 20)


# Глобальный экземпляр
level_resolver = LevelResolver()
