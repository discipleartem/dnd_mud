"""Реализация сервиса меню.

Следует Clean Architecture - бизнес-логика работы с меню.
Реализует интерфейс MenuServiceInterface.
"""

from typing import Optional, List, Dict, Any

from src.entities.menu_entity import MenuState, MenuItem, MenuActionType
from src.interfaces.services.menu_service_interface import MenuServiceInterface


class MenuService(MenuServiceInterface):
    """Сервис работы с меню.
    
    Следует Clean Architecture - содержит бизнес-логику
    управления состояниями меню и пунктами.
    """
    
    def create_menu_state(self, title: str, items: List[MenuItem]) -> MenuState:
        """Создать состояние меню.
        
        Args:
            title: Заголовок меню
            items: Список пунктов меню
            
        Returns:
            Состояние меню
        """
        menu_state = MenuState(
            title=title,
            items=items.copy(),
            selected_index=0
        )
        
        # Валидация созданного состояния
        menu_state.validate()
        
        return menu_state
    
    def add_menu_item(self, menu_state: MenuState, item: MenuItem) -> MenuState:
        """Добавить пункт в меню.
        
        Args:
            menu_state: Текущее состояние меню
            item: Новый пункт меню
            
        Returns:
            Обновленное состояние меню
        """
        # Валидация нового пункта
        item.validate()
        
        # Проверка уникальности ID
        existing_ids = [existing_item.id for existing_item in menu_state.items]
        if item.id in existing_ids:
            raise ValueError(f"Пункт меню с ID '{item.id}' уже существует")
        
        # Создаем новое состояние с добавленным пунктом
        new_items = menu_state.items + [item]
        new_state = MenuState(
            title=menu_state.title,
            items=new_items,
            selected_index=menu_state.selected_index,
            allow_back=menu_state.allow_back,
            allow_exit=menu_state.allow_exit
        )
        
        new_state.validate()
        return new_state
    
    def remove_menu_item(self, menu_state: MenuState, item_id: str) -> MenuState:
        """Удалить пункт из меню.
        
        Args:
            menu_state: Текущее состояние меню
            item_id: ID пункта для удаления
            
        Returns:
            Обновленное состояние меню
        """
        # Находим пункт для удаления
        item_to_remove = None
        for item in menu_state.items:
            if item.id == item_id:
                item_to_remove = item
                break
        
        if not item_to_remove:
            raise ValueError(f"Пункт меню с ID '{item_id}' не найден")
        
        # Создаем новое состояние без удаленного пункта
        new_items = [item for item in menu_state.items if item.id != item_id]
        
        # Корректируем выбранный индекс
        new_selected_index = menu_state.selected_index
        selectable_items = [item for item in new_items if item.is_selectable()]
        
        if new_selected_index >= len(selectable_items):
            new_selected_index = max(0, len(selectable_items) - 1)
        
        new_state = MenuState(
            title=menu_state.title,
            items=new_items,
            selected_index=new_selected_index,
            allow_back=menu_state.allow_back,
            allow_exit=menu_state.allow_exit
        )
        
        new_state.validate()
        return new_state
    
    def navigate_menu(self, menu_state: MenuState, direction: str) -> MenuState:
        """Навигация по меню.
        
        Args:
            menu_state: Текущее состояние меню
            direction: Направление ('up', 'down', 'home', 'end')
            
        Returns:
            Обновленное состояние меню
        """
        new_state = MenuState(
            title=menu_state.title,
            items=menu_state.items,
            selected_index=menu_state.selected_index,
            allow_back=menu_state.allow_back,
            allow_exit=menu_state.allow_exit
        )
        
        if direction == "up":
            new_state.move_selection(-1)
        elif direction == "down":
            new_state.move_selection(1)
        elif direction == "home":
            new_state.selected_index = 0
        elif direction == "end":
            selectable_items = new_state.get_selectable_items()
            new_state.selected_index = len(selectable_items) - 1
        else:
            raise ValueError(f"Неподдерживаемое направление навигации: {direction}")
        
        return new_state
    
    def select_item(self, menu_state: MenuState, selection: str) -> Optional[MenuItem]:
        """Выбрать пункт меню.
        
        Args:
            menu_state: Текущее состояние меню
            selection: Выбор (hotkey или index)
            
        Returns:
            Выбранный пункт или None
        """
        # Сначала пробуем найти по горячей клавише
        selected_item = menu_state.select_by_hotkey(selection)
        if selected_item:
            return selected_item
        
        # Затем пробуем по цифре
        if selection.isdigit():
            index = int(selection)
            selectable_items = menu_state.get_selectable_items()
            
            if 1 <= index <= len(selectable_items):
                menu_state.selected_index = index - 1
                return selectable_items[index - 1]
        
        return None
    
    def execute_item_action(self, item: MenuItem) -> Any:
        """Выполнить действие пункта меню.
        
        Args:
            item: Пункт меню
            
        Returns:
            Результат выполнения действия
        """
        if not item.is_enabled:
            return None
        
        if item.action_type == MenuActionType.ACTION and item.action:
            # Выполняем функцию действия
            return item.action()
        elif item.action_type == MenuActionType.NAVIGATION:
            # Возвращаем целевое меню
            return {"navigation": item.target_menu}
        elif item.action_type == MenuActionType.BACK:
            # Сигнал возврата
            return {"navigation": "back"}
        elif item.action_type == MenuActionType.EXIT:
            # Сигнал выхода
            return {"navigation": "exit"}
        
        return None
    
    def get_menu_context(self, menu_state: MenuState) -> Dict[str, Any]:
        """Получить контекст меню для рендеринга.
        
        Args:
            menu_state: Состояние меню
            
        Returns:
            Словарь с контекстом для рендеринга
        """
        return {
            "title": menu_state.title,
            "items": menu_state.items,
            "selected_index": menu_state.selected_index,
            "allow_back": menu_state.allow_back,
            "allow_exit": menu_state.allow_exit,
            "current_item": menu_state.get_current_item(),
            "selectable_items": menu_state.get_selectable_items(),
            "total_items": len(menu_state.items),
            "selectable_count": len(menu_state.get_selectable_items())
        }
    
    def validate_menu_state(self, menu_state: MenuState) -> bool:
        """Валидировать состояние меню.
        
        Args:
            menu_state: Состояние меню
            
        Returns:
            True если состояние валидно
        """
        try:
            menu_state.validate()
            return True
        except ValueError:
            return False
