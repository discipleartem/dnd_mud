"""Базовый класс для экранов."""

from abc import ABC, abstractmethod
from typing import Any

from interfaces.user_interface import UserInterface


class BaseScreen(ABC):
    """Базовый класс для всех экранов."""

    def __init__(self, ui: UserInterface) -> None:
        """Инициализация экрана."""
        self.ui = ui

    def _show_menu_items(self, items: list[str]) -> None:
        """Показать пункты меню."""
        for i, item in enumerate(items, 1):
            self.ui.print_menu_item(i, item)

    @abstractmethod
    def show(self) -> Any:
        """Показать экран и вернуть результат."""
        pass
