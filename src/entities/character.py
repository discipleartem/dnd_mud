"""Персонаж D&D - основная бизнес-сущность.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from dataclasses import dataclass


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

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        self._validate_character()

    def _validate_character(self) -> None:
        """Проверить корректность персонажа."""
        if len(self.name) < 2:
            raise ValueError("Имя слишком короткое")
        if not (1 <= self.level <= 20):
            raise ValueError("Неверный уровень")
        if self.hit_points < 0:
            raise ValueError("HP не могут быть отрицательными")
        if self.max_hit_points < 1:
            raise ValueError("Max HP должны быть положительными")

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
        if self.level >= 20:
            raise ValueError("Максимальный уровень достигнут")

        self.level += 1
        # Простые правила D&D: +2 HP за уровень
        self.max_hit_points += 2
        self.hit_points += 2

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
