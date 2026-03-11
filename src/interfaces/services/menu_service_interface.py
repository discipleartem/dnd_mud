"""Интерфейс сервиса меню.

Следует Clean Architecture - определяет контракт для работы с меню.
Не содержит реализации, только абстрактные методы.
"""

from abc import ABC, abstractmethod
from typing import Any

from src.entities.menu_entity import MenuItem, MenuState


class MenuServiceInterface(ABC):
    """Интерфейс сервиса работы с меню.

    Следует Clean Architecture - определяет контракт для
    бизнес-логики работы с меню без конкретной реализации.
    """

    @abstractmethod
    def create_menu_state(
        self, title: str, items: list[MenuItem]
    ) -> MenuState:
        """Создать состояние меню.

        Args:
            title: Заголовок меню
            items: Список пунктов меню

        Returns:
            Состояние меню
        """
        pass

    @abstractmethod
    def add_menu_item(
        self, menu_state: MenuState, item: MenuItem
    ) -> MenuState:
        """Добавить пункт в меню.

        Args:
            menu_state: Текущее состояние меню
            item: Новый пункт меню

        Returns:
            Обновленное состояние меню
        """
        pass

    @abstractmethod
    def remove_menu_item(
        self, menu_state: MenuState, item_id: str
    ) -> MenuState:
        """Удалить пункт из меню.

        Args:
            menu_state: Текущее состояние меню
            item_id: ID пункта для удаления

        Returns:
            Обновленное состояние меню
        """
        pass

    @abstractmethod
    def navigate_menu(
        self, menu_state: MenuState, direction: str
    ) -> MenuState:
        """Навигация по меню.

        Args:
            menu_state: Текущее состояние меню
            direction: Направление ('up', 'down', 'home', 'end')

        Returns:
            Обновленное состояние меню
        """
        pass

    @abstractmethod
    def select_item(
        self, menu_state: MenuState, selection: str
    ) -> MenuItem | None:
        """Выбрать пункт меню.

        Args:
            menu_state: Текущее состояние меню
            selection: Выбор (hotkey или index)

        Returns:
            Выбранный пункт или None
        """
        pass

    @abstractmethod
    def execute_item_action(self, item: MenuItem) -> Any:
        """Выполнить действие пункта меню.

        Args:
            item: Пункт меню

        Returns:
            Результат выполнения действия
        """
        pass

    @abstractmethod
    def get_menu_context(self, menu_state: MenuState) -> dict[str, Any]:
        """Получить контекст меню для рендеринга.

        Args:
            menu_state: Состояние меню

        Returns:
            Словарь с контекстом для рендеринга
        """
        pass

    @abstractmethod
    def validate_menu_state(self, menu_state: MenuState) -> bool:
        """Валидировать состояние меню.

        Args:
            menu_state: Состояние меню

        Returns:
            True если состояние валидно
        """
        pass
