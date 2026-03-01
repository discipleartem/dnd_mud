"""Бизнес-сущности D&D игры.

Следует принципам чистой архитектуры:
- Никаких внешних зависимостей
- Только бизнес-логика D&D
- Явное лучше неявного
- Простое лучше сложного
"""

from dataclasses import dataclass
from typing import Final


@dataclass
class Character:
    """Бизнес-сущность персонажа D&D.

    Содержит только бизнес-правила игры.
    Никаких зависимостей от базы данных или UI.
    """
    name: str
    level: int = 1
    hit_points: int = 10
    max_hit_points: int = 10

    # Константы D&D (YAGNI - только необходимое)
    MIN_LEVEL: Final[int] = 1
    MAX_LEVEL: Final[int] = 20
    MIN_NAME_LENGTH: Final[int] = 2

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        self._validate_character()

    def _validate_character(self) -> None:
        """Проверить корректность персонажа."""
        if not self.name or len(self.name) < self.MIN_NAME_LENGTH:
            raise ValueError(f"Имя должно содержать минимум {self.MIN_NAME_LENGTH} символа")

        if not self.MIN_LEVEL <= self.level <= self.MAX_LEVEL:
            raise ValueError(f"Уровень должен быть между {self.MIN_LEVEL} и {self.MAX_LEVEL}")

        if self.hit_points < 0:
            raise ValueError("Hit points не могут быть отрицательными")

        if self.max_hit_points < 1:
            raise ValueError("Max hit points должны быть положительными")

    def take_damage(self, damage: int) -> None:
        """Получить урон."""
        if damage < 0:
            raise ValueError("Урон не может быть отрицательным")

        self.hit_points = max(0, self.hit_points - damage)

    def heal(self, amount: int) -> None:
        """Восстановить здоровье."""
        if amount < 0:
            raise ValueError("Лечение не может быть отрицательным")

        self.hit_points = min(self.max_hit_points, self.hit_points + amount)

    def is_alive(self) -> bool:
        """Проверить, жив ли персонаж."""
        return self.hit_points > 0

    def level_up(self) -> None:
        """Повысить уровень."""
        if self.level >= self.MAX_LEVEL:
            raise ValueError(f"Максимальный уровень {self.MAX_LEVEL} достигнут")

        self.level += 1
        # Простые правила D&D: +2 HP за уровень
        hp_increase = 2
        self.max_hit_points += hp_increase
        self.hit_points += hp_increase

    def get_status(self) -> str:
        """Получить статус персонажа."""
        if not self.is_alive():
            return "Погиб"

        hp_ratio = self.hit_points / self.max_hit_points
        if hp_ratio >= 0.8:
            return "Здоров"
        elif hp_ratio >= 0.4:
            return "Ранен"
        else:
            return "Тяжело ранен"

    def __str__(self) -> str:
        """Строковое представление."""
        return f"{self.name} (Уровень {self.level}, HP: {self.hit_points}/{self.max_hit_points})"


@dataclass
class GameSession:
    """Бизнес-сущность сессии игры.

    Управляет состоянием игровой сессии.
    """
    player: Character
    session_name: str = "Новая игра"
    turn_count: int = 0

    def advance_turn(self) -> None:
        """Продвинуть на один ход."""
        self.turn_count += 1

    def get_session_info(self) -> str:
        """Получить информацию о сессии."""
        return f"{self.session_name} - Ход {self.turn_count}"

    def is_new_game(self) -> bool:
        """Проверить, новая ли это игра."""
        return self.turn_count == 0
