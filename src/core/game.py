"""Основной класс игры - координирует все слои."""

from __future__ import annotations
from pathlib import Path
from rich.console import Console


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

        self.data_dir = Path(__file__).parent.parent.parent / "data"  
        self.yaml_dir = self.data_dir / "yaml"
        self.saves_dir = self.data_dir / "saves"
        self.mods_dir = self.data_dir / "mods"
        self.adventures_dir = self.data_dir / "adventures"
            
        # TODO: Инициализация слоев по мере их создания
        # self.state_manager = StateManager()
        # self.window_manager = WindowManager()
        # self.localization_manager = LocalizationManager()
        
        
    
    def run(self) -> None:
        """Основной цикл игры."""
        self.console.print("DnD MUD запускается...")
        self.console.print(f"Директория данных: {self.data_dir}")
        
        # TODO: Здесь будет основной игровой цикл
        # state_manager.push_state(GameState.MAIN_MENU)
        
    def shutdown(self) -> None:
        """Корректное завершение работы."""
        # TODO: Сохранение состояния, очистка ресурсов
        self.console.print("Завершение работы...")
