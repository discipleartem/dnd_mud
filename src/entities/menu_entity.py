"""Сущность пункта меню.

Следует Clean Architecture - бизнес-сущность без внешних зависимостей.
Содержит бизнес-правила для пунктов меню.
"""

from dataclasses import dataclass
from typing import Optional, Callable, Any
from enum import Enum

from src.value_objects.base_validatable import BaseValidatable


class MenuActionType(Enum):
    """Тип действия пункта меню."""
    NAVIGATION = "navigation"  # Переход в другое меню
    ACTION = "action"        # Выполнение действия
    BACK = "back"            # Возврат в предыдущее меню
    EXIT = "exit"           # Выход из программы


@dataclass
class MenuItem(BaseValidatable):
    """Пункт меню.
    
    Бизнес-сущность представляющая один пункт в меню.
    Следует Clean Architecture - не зависит от внешних слоев.
    """
    id: str
    title: str
    description: Optional[str] = None
    action_type: MenuActionType = MenuActionType.ACTION
    target_menu: Optional[str] = None
    action: Optional[Callable[[], Any]] = None
    is_enabled: bool = True
    is_visible: bool = True
    hotkey: Optional[str] = None
    
    def validate(self) -> None:
        """Валидация бизнес-правил пункта меню.
        
        Raises:
            ValueError: Если пункт меню невалиден
        """
        if not self.id or not self.id.strip():
            raise ValueError("ID пункта меню не может быть пустым")
        
        if not self.title or not self.title.strip():
            raise ValueError("Заголовок пункта меню не может быть пустым")
        
        if len(self.title) > 50:
            raise ValueError("Заголовок пункта меню слишком длинный (макс 50 символов)")
        
        if self.action_type == MenuActionType.NAVIGATION and not self.target_menu:
            raise ValueError("Для пункта навигации необходимо указать target_menu")
        
        if self.action_type == MenuActionType.ACTION and not self.action:
            raise ValueError("Для пункта действия необходимо указать action")
    
    def is_selectable(self) -> bool:
        """Проверить, можно ли выбрать пункт меню.
        
        Returns:
            True если пункт можно выбрать
        """
        return self.is_enabled and self.is_visible
    
    def get_display_text(self) -> str:
        """Получить текст для отображения.
        
        Returns:
            Текст пункта меню для отображения
        """
        if self.hotkey:
            return f"[{self.hotkey}] {self.title}"
        return self.title


@dataclass
class MenuState(BaseValidatable):
    """Состояние меню.
    
    Бизнес-сущность представляющая текущее состояние меню.
    """
    title: str
    items: list[MenuItem]
    selected_index: int = 0
    allow_back: bool = True
    allow_exit: bool = True
    
    def validate(self) -> None:
        """Валидация состояния меню.
        
        Raises:
            ValueError: Если состояние меню невалидно
        """
        if not self.title or not self.title.strip():
            raise ValueError("Заголовок меню не может быть пустым")
        
        if not self.items:
            raise ValueError("Меню должно содержать хотя бы один пункт")
        
        if self.selected_index < 0 or self.selected_index >= len(self.items):
            raise ValueError("Индекс выбранного пункта вне диапазона")
        
        # Проверяем, что есть хотя бы один видимый пункт
        visible_items = [item for item in self.items if item.is_visible]
        if not visible_items:
            raise ValueError("Меню должно содержать хотя бы один видимый пункт")
    
    def get_selectable_items(self) -> list[MenuItem]:
        """Получить список выбираемых пунктов.
        
        Returns:
            Список выбираемых пунктов меню
        """
        return [item for item in self.items if item.is_selectable()]
    
    def get_current_item(self) -> Optional[MenuItem]:
        """Получить текущий выбранный пункт.
        
        Returns:
            Текущий пункт или None если нет выбираемых пунктов
        """
        selectable_items = self.get_selectable_items()
        if not selectable_items:
            return None
        
        if self.selected_index >= len(selectable_items):
            self.selected_index = len(selectable_items) - 1
        
        return selectable_items[self.selected_index]
    
    def move_selection(self, direction: int) -> bool:
        """Переместить выбор пункта меню.
        
        Args:
            direction: Направление движения (-1 вверх, +1 вниз)
            
        Returns:
            True если выбор был перемещен
        """
        selectable_items = self.get_selectable_items()
        if len(selectable_items) <= 1:
            return False
        
        old_index = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(selectable_items)
        
        return self.selected_index != old_index
    
    def select_by_hotkey(self, hotkey: str) -> Optional[MenuItem]:
        """Выбрать пункт по горячей клавише.
        
        Args:
            hotkey: Горячая клавиша
            
        Returns:
            Найденный пункт или None
        """
        for item in self.get_selectable_items():
            if item.hotkey and item.hotkey.lower() == hotkey.lower():
                return item
        return None
