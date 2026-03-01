"""Сессия игры - бизнес-сущность управления состоянием.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

from dataclasses import dataclass
from typing import Final

from .character import Character


@dataclass
class GameSession:
    """Бизнес-сущность сессии игры.

    Управляет состоянием игровой сессии.
    Никаких зависимостей от внешнего мира.
    """
    player: Character
    session_name: str = "Новая игра"
    turn_count: int = 0

    # Константы (YAGNI - только необходимое)
    MAX_TURNS: Final[int] = 999999

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        self._validate_session()

    def _validate_session(self) -> None:
        """Проверить корректность сессии."""
        if not self.player:
            raise ValueError("Персонаж обязателен для сессии")

        if not self.session_name or len(self.session_name.strip()) < 1:
            raise ValueError("Название сессии не может быть пустым")

        if self.turn_count < 0:
            raise ValueError("Количество ходов не может быть отрицательным")

    def advance_turn(self) -> None:
        """Продвинуть на один ход."""
        if self.turn_count >= self.MAX_TURNS:
            raise ValueError(f"Достигнуто максимальное количество ходов: {self.MAX_TURNS}")

        self.turn_count += 1

    def get_session_info(self) -> str:
        """Получить информацию о сессии."""
        return f"{self.session_name} - Ход {self.turn_count}"

    def is_new_game(self) -> bool:
        """Проверить, новая ли это игра."""
        return self.turn_count == 0

    def reset_session(self) -> None:
        """Сбросить сессию."""
        self.turn_count = 0
        self.session_name = "Новая игра"

    def __str__(self) -> str:
        """Строковое представление."""
        return f"{self.get_session_info()} - {self.player}"
