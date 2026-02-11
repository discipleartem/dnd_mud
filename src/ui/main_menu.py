"""Главное меню игры."""

from __future__ import annotations

from pathlib import Path

from src.core.state_manager import GameState
from src.core.window_manager import WindowManager
from src.ui.menu_base import MenuBase


class MainMenu(MenuBase):
    """Главное меню игры.
    
    Предоставляет доступ к основным функциям игры:
    - Новая игра
    - Продолжить (если есть сохранения)
    - Загрузить игру
    - Настройки
    - Выход
    """
    
    def __init__(self, window_manager: WindowManager) -> None:
        """Инициализация главного меню."""
        super().__init__(window_manager)
        self._saves_dir = Path(__file__).parent.parent.parent / "data" / "saves"
    
    def get_menu_items(self) -> list[str]:
        """Получить пункты главного меню."""
        items = ["Новая игра", "Настройки", "Выход"]
        
        # Добавляем "Продолжить" если есть сохранения
        if self.can_continue():
            items.insert(1, "Продолжить")
            items.insert(2, "Загрузить игру")
        
        return items
    
    def handle_selection(self, selected_index: int) -> GameState | None:
        """Обработать выбор пункта меню."""
        items = self.get_menu_items()
        
        if selected_index >= len(items):
            return None
        
        selected_item = items[selected_index]
        
        match selected_item:
            case "Новая игра":
                return GameState.CHARACTER_CREATION
            
            case "Продолжить":
                # TODO: Загрузить последнее сохранение
                return GameState.ADVENTURE
            
            case "Загрузить игру":
                return GameState.LOAD_GAME
            
            case "Настройки":
                return GameState.SETTINGS
            
            case "Выход":
                return GameState.EXIT
            
            case _:
                return None
    
    def can_continue(self) -> bool:
        """Проверить наличие сохраненных игр."""
        if not self._saves_dir.exists():
            return False
        
        # Ищем файлы сохранений (.json)
        save_files = list(self._saves_dir.glob("*.json"))
        return len(save_files) > 0
    
    def _render_title(self) -> None:
        """Отрисовать заголовок главного меню."""
        subtitle = ""
        if self.can_continue():
            save_count = len(list(self._saves_dir.glob("*.json")))
            subtitle = f"Найдено сохранений: {save_count}"
        
        self.window_manager.show_title("Главное меню", subtitle)
    
    def _render_footer(self) -> None:
        """Отрисовать подсказки управления."""
        hints = [
            "↑/↓ - Навигация",
            "Enter - Выбрать",
            "Esc - Выход"
        ]
        
        # Дополнительные подсказки если есть сохранения
        if self.can_continue():
            hints.append("F5 - Быстрая загрузка")
        
        # Адаптируем под размер терминала
        if self.window_manager._size.width < 100:
            # Компактные подсказки
            if self.can_continue():
                hints = ["↑/↓ Навигация", "Enter Выбрать", "Esc Выход", "F5 Загрузка"]
            else:
                hints = ["↑/↓ Навигация", "Enter Выбрать", "Esc Выход"]
        
        hint_text = " | ".join(hints)
        self.window_manager.print_text(hint_text, color="cyan", wrap=False)
