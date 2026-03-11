"""DTO для передачи данных меню между слоями.

Следует Clean Architecture - объекты для передачи данных.
Используются для коммуникации между Controller и Use Case.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

from src.entities.menu_entity import MenuActionType


class MenuNavigationDirection(Enum):
    """Направление навигации меню."""
    UP = "up"
    DOWN = "down"
    HOME = "home"
    END = "end"


@dataclass
class MenuControllerRequest:
    """Запрос к контроллеру меню."""
    action: str
    menu_id: Optional[str] = None
    selection: Optional[str] = None
    direction: Optional[MenuNavigationDirection] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class MenuItemDTO:
    """DTO для пункта меню."""
    id: str
    title: str
    description: Optional[str] = None
    action_type: MenuActionType = MenuActionType.ACTION
    target_menu: Optional[str] = None
    is_enabled: bool = True
    is_visible: bool = True
    hotkey: Optional[str] = None
    index: Optional[int] = None
    action: Optional[Any] = None  # Добавляем поле action
    
    def get_display_text(self) -> str:
        """Получить текст для отображения.
        
        Returns:
            Текст пункта меню для отображения
        """
        return self.title
    
    @classmethod
    def from_entity(cls, entity, index: Optional[int] = None) -> 'MenuItemDTO':
        """Создать DTO из сущности.
        
        Args:
            entity: Сущность пункта меню
            index: Индекс пункта
            
        Returns:
            DTO пункта меню
        """
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            action_type=entity.action_type,
            target_menu=entity.target_menu,
            is_enabled=entity.is_enabled,
            is_visible=entity.is_visible,
            hotkey=entity.hotkey,
            index=index,
            action=entity.action  # Копируем действие из сущности
        )


@dataclass
class MenuStateDTO:
    """DTO для состояния меню."""
    title: str
    items: List[MenuItemDTO]
    selected_index: int = 0
    allow_back: bool = True
    allow_exit: bool = True
    total_items: int = 0
    selectable_items: int = 0
    
    @classmethod
    def from_entity(cls, entity) -> 'MenuStateDTO':
        """Создать DTO из сущности.
        
        Args:
            entity: Сущность состояния меню
            
        Returns:
            DTO состояния меню
        """
        items = []
        for i, item in enumerate(entity.items):
            item_dto = MenuItemDTO.from_entity(item, i + 1)
            items.append(item_dto)
        
        return cls(
            title=entity.title,
            items=items,
            selected_index=entity.selected_index,
            allow_back=entity.allow_back,
            allow_exit=entity.allow_exit,
            total_items=len(entity.items),
            selectable_items=len(entity.get_selectable_items())
        )


@dataclass
class MenuControllerResponse:
    """Ответ контроллера меню."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    menu_state: Optional[MenuStateDTO] = None
    action_result: Optional[Any] = None
    next_menu: Optional[str] = None
    should_exit: bool = False


@dataclass
class MenuRenderRequest:
    """Запрос на рендеринг меню."""
    menu_state: MenuStateDTO
    use_colors: bool = True
    clear_screen: bool = True
    show_help: bool = True


@dataclass
class MenuRenderResponse:
    """Ответ рендеринга меню."""
    rendered_text: str
    width: int
    height: int
    has_colors: bool


@dataclass
class MenuSelectionRequest:
    """Запрос на выбор пункта меню."""
    menu_state: MenuStateDTO
    selection: str  # Может быть цифра или hotkey


@dataclass
class MenuSelectionResponse:
    """Ответ выбора пункта меню."""
    success: bool
    selected_item: Optional[MenuItemDTO] = None
    action_result: Optional[Any] = None
    error_message: Optional[str] = None
