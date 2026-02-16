"""
Модуль главного меню D&D MUD.

Реализует главное меню игры с выбором опций.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Callable, Dict, List, Any
from enum import Enum

# Добавляем src в Python path для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.renderer import renderer
from src.ui.input_handler import input_handler


class MenuOption(Enum):
    """Опции главного меню."""
    NEW_GAME = "new_game"
    LOAD_GAME = "load_game"
    SETTINGS = "settings"
    EXIT = "exit"


class MainMenu:
    """Класс главного меню игры."""
    
    def __init__(self) -> None:
        """Инициализация главного меню."""
        self.selected_index: int = 0
        self.menu_options: List[Dict[str, str]] = [
            {"text": "Новая игра", "action": MenuOption.NEW_GAME},
            {"text": "Загрузить игру", "action": MenuOption.LOAD_GAME},
            {"text": "Настройки", "action": MenuOption.SETTINGS},
            {"text": "Выход", "action": MenuOption.EXIT},
        ]
        
        # Callback функции для обработки выбора
        self.callbacks: Dict[MenuOption, Callable] = {}
    
    def set_callback(self, option: MenuOption, callback: Callable) -> None:
        """Устанавливает callback функцию для опции меню."""
        self.callbacks[option] = callback
    
    def show(self) -> None:
        """Отображает главное меню."""
        # Отображаем заголовок
        renderer.show_title("Dungeons & Dragons MUD", "Текстовая ролевая игра")
        
        # Отображаем меню
        renderer.show_menu("Главное меню", self.menu_options)
        
        # Отображаем управление
        print("Управление:")
        print("• Введите номер пункта меню (1-4)")
        print("• Нажмите Enter для выбора")
        print("• Ctrl+C для выхода")
        print()
    
    def run(self) -> MenuOption:
        """Запускает главное меню и возвращает выбранный результат."""
        try:
            while True:
                self.show()
                
                # Получаем числовой выбор от пользователя
                choice = input_handler.get_menu_choice(len(self.menu_options))
                
                # Выбираем пункт меню (choice - 1 потому что нумерация с 1)
                self.selected_index = choice - 1
                selected_option = self.menu_options[self.selected_index]
                menu_action = selected_option["action"]
                
                # Если выбран выход
                if menu_action == MenuOption.EXIT:
                    return MenuOption.EXIT
                
                # Обрабатываем другие опции
                if menu_action in self.callbacks:
                    callback = self.callbacks[menu_action]
                    callback()
                
                # Для других опций пока просто выходим из меню
                # В будущем здесь будет логика обработки
                return menu_action
                
        except KeyboardInterrupt:
            # Обработка Ctrl+C
            return MenuOption.EXIT
        except Exception as e:
            renderer.show_error(f"Ошибка в меню: {e}")
            return MenuOption.EXIT
    
    def show_load_game_menu(self) -> Optional[str]:
        """Отображает меню загрузки игры."""
        # Здесь будет логика загрузки сохранений
        renderer.show_info("Функция загрузки игры пока не реализована")
        renderer.get_input("Нажмите Enter для возврата в главное меню...")
        return None
    
    def show_settings_menu(self) -> None:
        """Отображает меню настроек."""
        # Здесь будет логика настроек
        renderer.show_info("Функция настроек пока не реализована")
        renderer.get_input("Нажмите Enter для возврата в главное меню...")


class NewGameMenu:
    """Класс меню создания новой игры."""
    
    def show(self) -> None:
        """Отображает меню создания новой игры."""
        renderer.clear_screen()
        renderer.show_title("Создание персонажа", "Шаг за шагом создайте своего героя")
        
        # Здесь будет логика создания персонажа
        renderer.show_info("Функция создания персонажа будет реализована в следующей версии")
        renderer.get_input("Нажмите Enter для возврата в главное меню...")


# Удобные функции для использования в других частях приложения
def show_main_menu() -> MenuOption:
    """Отображает главное меню и возвращает выбор пользователя."""
    menu = MainMenu()
    return menu.run()


def show_new_game_menu() -> None:
    """Отображает меню создания новой игры."""
    menu = NewGameMenu()
    menu.show()


def show_load_game_menu() -> Optional[str]:
    """Отображает меню загрузки игры."""
    menu = MainMenu()
    return menu.show_load_game_menu()


def show_settings_menu() -> None:
    """Отображает меню настроек."""
    menu = MainMenu()
    menu.show_settings_menu()