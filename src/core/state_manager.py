"""
State Manager - управление состоянием игры.

Паттерны: State, Memento
Принципы: SRP, OCP
"""

import json
import os
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path


class GameState(Enum):
    """Состояния игры."""
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    ADVENTURE = "adventure"
    COMBAT = "combat"
    INVENTORY = "inventory"
    REST = "rest"
    SETTINGS = "settings"
    LOAD_GAME = "load_game"
    EXIT = "exit"


@dataclass
class GameSnapshot:
    """
    Снимок состояния игры (Memento паттерн).

    Используется для сохранения/восстановления состояния.
    """
    state: str
    data: Dict[str, Any]
    timestamp: str


class StateManager:
    """
    Управление состояниями игры.

    Паттерны:
    - State: управление переходами между состояниями
    - Memento: сохранение и восстановление состояния
    - Singleton: единственный экземпляр менеджера
    """

    _instance: Optional['StateManager'] = None
    _initialized: bool = False

    CONTINUE_SAVE_PATH = "data/saves/continue.json"

    def __new__(cls) -> 'StateManager':
        """Singleton паттерн."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Инициализация менеджера состояний."""
        if self._initialized:
            return

        self._current_state: GameState = GameState.MAIN_MENU
        self._previous_state: Optional[GameState] = None
        self._state_data: Dict[str, Any] = {}
        self._initialized = True

        # Создание директории для сохранений
        Path("data/saves").mkdir(parents=True, exist_ok=True)

    def set_state(self, state: GameState, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Установка нового состояния.

        Args:
            state: новое состояние
            data: дополнительные данные состояния
        """
        self._previous_state = self._current_state
        self._current_state = state

        if data:
            self._state_data.update(data)

    def get_state(self) -> GameState:
        """Получение текущего состояния."""
        return self._current_state

    def get_previous_state(self) -> Optional[GameState]:
        """Получение предыдущего состояния."""
        return self._previous_state

    def get_state_data(self, key: str, default: Any = None) -> Any:
        """
        Получение данных состояния.

        Args:
            key: ключ данных
            default: значение по умолчанию

        Returns:
            Any: значение данных или default
        """
        return self._state_data.get(key, default)

    def set_state_data(self, key: str, value: Any) -> None:
        """
        Установка данных состояния.

        Args:
            key: ключ данных
            value: значение
        """
        self._state_data[key] = value

    def clear_state_data(self) -> None:
        """Очистка всех данных состояния."""
        self._state_data.clear()

    def can_continue(self) -> bool:
        """
        Проверка наличия активной игры для продолжения.

        Returns:
            bool: True если есть сохранение для продолжения
        """
        return os.path.exists(self.CONTINUE_SAVE_PATH)

    def save_continue_state(self, game_data: Dict[str, Any]) -> bool:
        """
        Сохранение состояния для функции "Продолжить".

        Args:
            game_data: данные игры для сохранения

        Returns:
            bool: успешность сохранения
        """
        try:
            from datetime import datetime

            snapshot = {
                "state": self._current_state.value,
                "data": game_data,
                "timestamp": datetime.now().isoformat(),
                "version": "0.1.0"
            }

            # Атомарное сохранение (сначала во временный файл)
            temp_path = self.CONTINUE_SAVE_PATH + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)

            # Переименование после успешной записи
            if os.path.exists(self.CONTINUE_SAVE_PATH):
                # Backup предыдущего сохранения
                backup_path = self.CONTINUE_SAVE_PATH + ".bak"
                os.replace(self.CONTINUE_SAVE_PATH, backup_path)

            os.replace(temp_path, self.CONTINUE_SAVE_PATH)
            return True

        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False

    def load_continue_state(self) -> Optional[Dict[str, Any]]:
        """
        Загрузка состояния для продолжения игры.

        Returns:
            Optional[Dict]: данные сохранения или None
        """
        if not self.can_continue():
            return None

        try:
            with open(self.CONTINUE_SAVE_PATH, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)

            # Валидация версии
            if snapshot.get("version") != "0.1.0":
                print("Предупреждение: версия сохранения отличается")

            # Восстановление состояния
            state_value = snapshot.get("state")
            if state_value:
                try:
                    self._current_state = GameState(state_value)
                except ValueError:
                    self._current_state = GameState.ADVENTURE

            data = snapshot.get("data", {})
            return data if isinstance(data, dict) else {}

        except json.JSONDecodeError as e:
            print(f"Ошибка при загрузке сохранения: повреждённый файл ({e})")

            # Попытка загрузить backup
            backup_path = self.CONTINUE_SAVE_PATH + ".bak"
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        snapshot = json.load(f)
                    print("Загружен резервный файл сохранения")
                    data = snapshot.get("data", {})
                    return data if isinstance(data, dict) else {}
                except Exception:
                    pass

            return None

        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            return None

    def delete_continue_state(self) -> bool:
        """
        Удаление сохранения для продолжения.

        Returns:
            bool: успешность удаления
        """
        try:
            if os.path.exists(self.CONTINUE_SAVE_PATH):
                os.remove(self.CONTINUE_SAVE_PATH)

            # Удаление backup
            backup_path = self.CONTINUE_SAVE_PATH + ".bak"
            if os.path.exists(backup_path):
                os.remove(backup_path)

            return True
        except Exception as e:
            print(f"Ошибка при удалении сохранения: {e}")
            return False

    def create_snapshot(self) -> GameSnapshot:
        """
        Создание снимка текущего состояния (Memento).

        Returns:
            GameSnapshot: снимок состояния
        """
        from datetime import datetime

        return GameSnapshot(
            state=self._current_state.value,
            data=self._state_data.copy(),
            timestamp=datetime.now().isoformat()
        )

    def restore_snapshot(self, snapshot: GameSnapshot) -> None:
        """
        Восстановление состояния из снимка.

        Args:
            snapshot: снимок для восстановления
        """
        try:
            self._current_state = GameState(snapshot.state)
            self._state_data = snapshot.data.copy()
        except ValueError as e:
            print(f"Ошибка восстановления состояния: {e}")
            self._current_state = GameState.MAIN_MENU


# Глобальный экземпляр
state_manager = StateManager()