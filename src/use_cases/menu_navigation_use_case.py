"""Use Case для навигации по меню.

Следует Clean Architecture - содержит бизнес-логику навигации.
Зависит только от Entities и Interfaces.
"""

from typing import Optional, Any, Dict, List

from src.entities.menu_entity import MenuState, MenuItem, MenuActionType
from src.interfaces.services.menu_service_interface import MenuServiceInterface


class MenuNavigationUseCase:
    """Use Case для навигации по меню.
    
    Следует Clean Architecture - содержит бизнес-логику
    навигации по пунктам меню и выполнения действий.
    """
    
    def __init__(self, menu_service: MenuServiceInterface) -> None:
        """Инициализация Use Case.
        
        Args:
            menu_service: Сервис работы с меню
        """
        self._menu_service = menu_service
    
    def create_menu(self, title: str, items: List[MenuItem]) -> MenuState:
        """Создать новое меню.
        
        Args:
            title: Заголовок меню
            items: Список пунктов меню
            
        Returns:
            Состояние созданного меню
            
        Raises:
            ValueError: Если меню невалидно
        """
        menu_state = self._menu_service.create_menu_state(title, items)
        
        if not self._menu_service.validate_menu_state(menu_state):
            raise ValueError(f"Невозможно создать меню: {title}")
        
        return menu_state
    
    def navigate_up(self, menu_state: MenuState) -> MenuState:
        """Переместить выбор вверх.
        
        Args:
            menu_state: Текущее состояние меню
            
        Returns:
            Обновленное состояние меню
        """
        return self._menu_service.navigate_menu(menu_state, "up")
    
    def navigate_down(self, menu_state: MenuState) -> MenuState:
        """Переместить выбор вниз.
        
        Args:
            menu_state: Текущее состояние меню
            
        Returns:
            Обновленное состояние меню
        """
        return self._menu_service.navigate_menu(menu_state, "down")
    
    def select_by_index(self, menu_state: MenuState, index: int) -> Optional[MenuItem]:
        """Выбрать пункт по индексу.
        
        Args:
            menu_state: Текущее состояние меню
            index: Индекс пункта (1-based для пользовательского ввода)
            
        Returns:
            Выбранный пункт или None
        """
        # Конвертируем 1-based индекс в 0-based
        zero_based_index = index - 1
        selectable_items = menu_state.get_selectable_items()
        
        if 0 <= zero_based_index < len(selectable_items):
            menu_state.selected_index = zero_based_index
            return selectable_items[zero_based_index]
        
        return None
    
    def select_by_hotkey(self, menu_state: MenuState, hotkey: str) -> Optional[MenuItem]:
        """Выбрать пункт по горячей клавише.
        
        Args:
            menu_state: Текущее состояние меню
            hotkey: Горячая клавиша
            
        Returns:
            Выбранный пункт или None
        """
        return self._menu_service.select_item(menu_state, hotkey)
    
    def execute_current_item(self, menu_state: MenuState) -> Any:
        """Выполнить действие текущего пункта.
        
        Args:
            menu_state: Текущее состояние меню
            
        Returns:
            Результат выполнения действия
            
        Raises:
            ValueError: Если нет выбранного пункта
        """
        current_item = menu_state.get_current_item()
        if not current_item:
            raise ValueError("Нет выбранного пункта меню")
        
        return self._menu_service.execute_item_action(current_item)
    
    def handle_selection(self, menu_state: MenuState, selection: str) -> tuple[Optional[MenuItem], Any]:
        """Обработать выбор пользователя.
        
        Args:
            menu_state: Текущее состояние меню
            selection: Выбор пользователя (цифра или hotkey)
            
        Returns:
            Кортеж (выбранный пункт, результат выполнения)
        """
        selected_item = None
        result = None
        
        # Пробуем выбрать по горячей клавише
        selected_item = self.select_by_hotkey(menu_state, selection)
        
        # Если не получилось, пробуем по цифре
        if not selected_item and selection.isdigit():
            index = int(selection)
            selected_item = self.select_by_index(menu_state, index)
        
        # Если пункт выбран, выполняем действие
        if selected_item:
            result = self._menu_service.execute_item_action(selected_item)
        
        return selected_item, result
    
    def get_render_context(self, menu_state: MenuState) -> Dict[str, Any]:
        """Получить контекст для рендеринга меню.
        
        Args:
            menu_state: Текущее состояние меню
            
        Returns:
            Словарь с контекстом для рендеринга
        """
        context = self._menu_service.get_menu_context(menu_state)
        
        # Добавляем полезную информацию для рендеринга
        context.update({
            "selectable_items": menu_state.get_selectable_items(),
            "current_item": menu_state.get_current_item(),
            "total_selectable": len(menu_state.get_selectable_items()),
            "has_navigation": len(menu_state.get_selectable_items()) > 1,
            "allow_back": menu_state.allow_back,
            "allow_exit": menu_state.allow_exit
        })
        
        return context
    
    def add_item(self, menu_state: MenuState, item: MenuItem) -> MenuState:
        """Добавить пункт в меню.
        
        Args:
            menu_state: Текущее состояние меню
            item: Новый пункт меню
            
        Returns:
            Обновленное состояние меню
        """
        return self._menu_service.add_menu_item(menu_state, item)
    
    def remove_item(self, menu_state: MenuState, item_id: str) -> MenuState:
        """Удалить пункт из меню.
        
        Args:
            menu_state: Текущее состояние меню
            item_id: ID пункта для удаления
            
        Returns:
            Обновленное состояние меню
        """
        return self._menu_service.remove_menu_item(menu_state, item_id)
