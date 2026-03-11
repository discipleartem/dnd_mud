"""DTO для передачи данных меню между слоями.

Следует Clean Architecture - объекты для передачи данных.
Используются для коммуникации между Controller и Use Case.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.entities.menu_entity import MenuActionType, MenuItem, MenuState


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
    menu_id: str | None = None
    selection: str | None = None
    direction: MenuNavigationDirection | None = None
    context: dict[str, Any] | None = None


@dataclass
class MenuItemDTO:
    """DTO для пункта меню."""

    id: str
    title: str
    description: str | None = None
    action_type: MenuActionType = MenuActionType.ACTION
    target_menu: str | None = None
    is_enabled: bool = True
    is_visible: bool = True
    hotkey: str | None = None
    index: int | None = None
    action: Any | None = None  # Добавляем поле action

    def get_display_text(self) -> str:
        """Получить текст для отображения.

        Returns:
            Текст пункта меню для отображения
        """
        if self.hotkey:
            return f"[{self.hotkey.upper()}] {self.title}"
        return self.title

    def to_entity(self) -> "MenuItem":
        """Преобразовать DTO в сущность.

        Returns:
            Сущность пункта меню
        """
        return MenuItem(
            id=self.id,
            title=self.title,
            description=self.description,
            action_type=self.action_type,
            target_menu=self.target_menu,
            is_enabled=self.is_enabled,
            is_visible=self.is_visible,
            hotkey=self.hotkey,
            action=self.action,
        )

    @classmethod
    def from_entity(cls, entity, index: int | None = None) -> "MenuItemDTO":
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
            action=entity.action,  # Копируем действие из сущности
        )


@dataclass
class MenuStateDTO:
    """DTO для состояния меню."""

    title: str
    items: list[MenuItemDTO]
    selected_index: int = 0
    allow_back: bool = True
    allow_exit: bool = True
    total_items: int = 0
    _selectable_items_count: int = (
        0  # Внутреннее поле для количества выбираемых пунктов
    )

    def __post_init__(self):
        """Валидация после инициализации."""
        if not self.title.strip():
            raise ValueError("Заголовок меню не может быть пустым")

        if not self.items:
            raise ValueError("Список пунктов меню не может быть пустым")

        if self.selected_index < 0 or self.selected_index >= len(self.items):
            raise ValueError("Индекс выбранного пункта вне диапазона")

        # Обновляем total_items на основе реального количества
        self.total_items = len(self.items)

    @classmethod
    def from_entity(cls, entity) -> "MenuStateDTO":
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
            _selectable_items_count=len(entity.get_selectable_items()),
        )

    def to_entity(self) -> "MenuState":
        """Преобразовать DTO в сущность.

        Returns:
            Сущность состояния меню
        """
        items = [item.to_entity() for item in self.items]

        return MenuState(
            title=self.title,
            items=items,
            selected_index=self.selected_index,
            allow_back=self.allow_back,
            allow_exit=self.allow_exit,
        )

    @property
    def selectable_items(self) -> list[MenuItemDTO]:
        """Получить выбираемые пункты меню.

        Returns:
            Список выбираемых пунктов
        """
        return [
            item for item in self.items if item.is_enabled and item.is_visible
        ]

    def get_current_item(self) -> MenuItemDTO | None:
        """Получить текущий выбранный пункт.

        Returns:
            Текущий пункт или None
        """
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            return item if item.is_enabled and item.is_visible else None
        return None


@dataclass
class MenuControllerResponse:
    """Ответ контроллера меню."""

    success: bool
    message: str
    data: dict[str, Any] | None = None
    menu_state: MenuStateDTO | None = None
    action_result: Any | None = None
    next_menu: str | None = None
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
    selected_item: MenuItemDTO | None = None
    action_result: Any | None = None
    error_message: str | None = None
