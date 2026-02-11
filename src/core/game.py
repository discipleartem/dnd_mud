"""Основной класс игры - координирует все слои."""

from __future__ import annotations
from pathlib import Path
from rich.console import Console

from core.state import StateManager
from core.window_manager import WindowManager
from ui.main_menu import MainMenu
from data.localization_manager import LocalizationManager


class SingletonMeta(type):
    _instances: dict[type, object] = {}
    
    def __call__(cls, *args, **kwargs) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Game(metaclass=SingletonMeta):
    """Основной класс игры."""

    def __init__(self) -> None:
        # Пути к данным
        if hasattr(self, '_initialized'):
            return

        self.console = Console()
        self._initialized = True
        
        # Сначала устанавливаем пути
        self.data_dir = Path(__file__).parent.parent.parent / "data"  
        self.yaml_dir = self.data_dir / "yaml"
        self.saves_dir = self.data_dir / "saves"
        self.mods_dir = self.data_dir / "mods"
        self.adventures_dir = self.data_dir / "adventures"
        
        # Потом создаем объекты
        self.state_manager = StateManager()
        self.window_manager = WindowManager(self.console)
        self.main_menu = MainMenu(self.window_manager)

        self.localization_manager = LocalizationManager(self.console)
        self.localization_manager.add_source(self.yaml_dir / "localization.yaml", priority=0)

        
        
    
    def run(self) -> None:
        """Основной цикл игры."""
        if not self.window_manager.check_terminal_size():
            self.window_manager.show_error(
                "Терминал слишком маленький! Минимум 80x24"
            )
            return
        
        self.window_manager.show_title("DnD MUD", "Текстовая RPG по D&D 5e")
        self.console.print("DnD MUD запускается...")
        self.console.print(f"Директория данных: {self.data_dir}")
        
        # TODO: Здесь будет основной игровой цикл
        # state_manager.push_state(GameState.MAIN_MENU)
        
    def shutdown(self) -> None:
        """Корректное завершение работы."""
        # TODO: Сохранение состояния, очистка ресурсов
        self.console.print("Завершение работы...")
