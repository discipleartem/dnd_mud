"""Управление состояниями игры - State паттерн."""

from __future__ import annotations

from enum import Enum, auto
from typing import Any


class GameState(Enum):
    """Состояния игры."""
    MAIN_MENU = auto()
    CHARACTER_CREATION = auto()
    ADVENTURE = auto()
    COMBAT = auto()
    INVENTORY = auto()
    REST = auto()
    SETTINGS = auto()
    LOAD_GAME = auto()
    EXIT = auto()


class StateManager:
    """Управление состояниями игры - State паттерн.
    
    Реализует стек состояний для навигации по меню
    и управления текущим активным состоянием.
    """
    
    def __init__(self) -> None:
        """Инициализация менеджера состояний."""
        self._states: list[GameState] = []
        self._current_state: GameState | None = None
    
    def push_state(self, state: GameState) -> None:
        """Добавить состояние в стек.
        
        Args:
            state: Новое состояние для активации
        """
        if self._current_state == state:
            return  # Уже в этом состоянии
            
        self._states.append(state)
        self._current_state = state
    
    def pop_state(self) -> GameState | None:
        """Удалить текущее состояние и вернуться к предыдущему.
        
        Returns:
            GameState | None: Предыдущее состояние или None если стек пуст
        """
        if len(self._states) <= 1:
            return None  # Некуда возвращаться
            
        self._states.pop()  # Удаляем текущее
        self._current_state = self._states[-1] if self._states else None
        return self._current_state
    
    def get_current_state(self) -> GameState | None:
        """Получить текущее активное состояние.
        
        Returns:
            GameState | None: Текущее состояние
        """
        return self._current_state
    
    def is_state(self, state: GameState) -> bool:
        """Проверить, является ли указанное состояние текущим.
        
        Args:
            state: Состояние для проверки
            
        Returns:
            bool: True если это текущее состояние
        """
        return self._current_state == state
    
    def clear_states(self) -> None:
        """Очистить стек состояний.
        
        Полезно для перезапуска или перехода в главное меню.
        """
        self._states.clear()
        self._current_state = None
    
    def get_state_history(self) -> list[GameState]:
        """Получить историю состояний (для отладки).
        
        Returns:
            list[GameState]: Копия стека состояний
        """
        return self._states.copy()
    
    def __str__(self) -> str:
        """Строковое представление текущего состояния."""
        if self._current_state:
            return f"StateManager(current={self._current_state.name}, stack_size={len(self._states)})"
        return "StateManager(no_current_state)"
