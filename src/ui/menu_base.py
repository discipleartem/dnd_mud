"""Базовый класс меню - Template Method паттерн."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.state_manager import GameState
from src.core.window_manager import WindowManager


class MenuBase(ABC):
    """Базовый класс для всех меню.
    
    Реализует Template Method паттерн:
    - Определяет общую логику отрисовки
    - Дочерние классы реализуют конкретное поведение
    """
    
    def __init__(self, window_manager: WindowManager) -> None:
        """Инициализация меню."""
        self.window_manager = window_manager
        self._selected_index = 0
        self._menu_items: list[str] = []
    
    @abstractmethod
    def get_menu_items(self) -> list[str]:
        """Получить список пунктов меню.
        
        Returns:
            list[str]: Пункты меню для отображения
        """
        pass
    
    @abstractmethod
    def handle_selection(self, selected_index: int) -> GameState | None:
        """Обработать выбор пункта меню.
        
        Args:
            selected_index: Индекс выбранного пункта
            
        Returns:
            GameState | None: Новое состояние или None для продолжения
        """
        pass
    
    @abstractmethod
    def can_continue(self) -> bool:
        """Проверить возможность продолжения игры.
        
        Returns:
            bool: True если есть сохраненная игра
        """
        return False
    
    def render(self) -> None:
        """Отрисовать меню - Template Method."""
        # Получаем пункты от дочернего класса
        items = self.get_menu_items()
        
        # Адаптивная отрисовка с учетом размера терминала
        if not self.window_manager.check_terminal_size():
            self.window_manager.show_error(
                "Терминал слишком маленький! Минимум 80x24"
            )
            return
        
        # Отрисовка заголовка меню
        self._render_title()
        
        # Отрисовка пунктов меню
        self.window_manager.show_menu(items, self._selected_index)
        
        # Отрисовка подсказок
        self._render_footer()
    
    def _render_title(self) -> None:
        """Отрисовать заголовок меню."""
        # Метод может быть переопределен в дочерних классах
        self.window_manager.show_title("DnD MUD", "Текстовая RPG")
    
    def _render_footer(self) -> None:
        """Отрисовать подсказки управления."""
        hints = [
            "↑/↓ - Навигация",
            "Enter - Выбрать",
            "Esc - Выход"
        ]
        
        # Адаптируем подсказки под размер терминала
        if self.window_manager._size.width < 100:
            hints = ["↑/↓ - Навигация", "Enter - Выбрать", "Esc - Выход"]
        
        hint_text = " | ".join(hints)
        self.window_manager.print_text(hint_text, color="cyan", wrap=False)
    
    def move_selection_up(self) -> None:
        """Переместить выделение вверх."""
        if self._selected_index > 0:
            self._selected_index -= 1
        else:
            self._selected_index = len(self.get_menu_items()) - 1  # Зациклить
    
    def move_selection_down(self) -> None:
        """Переместить выделение вниз."""
        max_index = len(self.get_menu_items()) - 1
        if self._selected_index < max_index:
            self._selected_index += 1
        else:
            self._selected_index = 0  # Зациклить
    
    def get_selected_index(self) -> int:
        """Получить текущий выделенный индекс."""
        return self._selected_index
    
    def reset_selection(self) -> None:
        """Сбросить выделение в начало."""
        self._selected_index = 0
