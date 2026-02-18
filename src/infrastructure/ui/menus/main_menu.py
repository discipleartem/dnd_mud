"""Модуль главного меню D&D MUD."""

from enum import Enum
from typing import Callable, Dict, List

from ...infrastructure.ui.renderer import renderer
from ...infrastructure.ui.input_handler import input_handler
from .character_creation import CharacterCreationController


class MenuOption(Enum):
    """Опции главного меню."""
    NEW_GAME = "new_game"
    LOAD_GAME = "load_game"
    SETTINGS = "settings"
    EXIT = "exit"


class MainMenu:
    """Простое главное меню игры."""
    
    def __init__(self) -> None:
        self.selected_index = 0
        self.menu_options = [
            {"text": "Новая игра", "action": MenuOption.NEW_GAME},
            {"text": "Загрузить игру", "action": MenuOption.LOAD_GAME},
            {"text": "Настройки", "action": MenuOption.SETTINGS},
            {"text": "Выход", "action": MenuOption.EXIT},
        ]
        self.callbacks = {}
    
    def set_callback(self, option: MenuOption, callback: Callable) -> None:
        """Устанавливает callback функцию для опции меню."""
        self.callbacks[option] = callback
    
    def display(self) -> None:
        """Отображает меню."""
        renderer.clear_screen()
        renderer.render_title("D&D MUD - Главное меню")
        
        print("\n" + "="*50)
        for i, option in enumerate(self.menu_options):
            marker = "►" if i == self.selected_index else " "
            print(f"{marker} {i+1}. {option['text']}")
        print("="*50)
        
        print("\nИспользуйте:")
        print("  W/↑ - вверх")
        print("  S/↓ - вниз")
        print("  Enter - выбрать")
        print("  Q - выход")
    
    def move_up(self) -> None:
        """Перемещает курсор вверх."""
        self.selected_index = (self.selected_index - 1) % len(self.menu_options)
    
    def move_down(self) -> None:
        """Перемещает курсор вниз."""
        self.selected_index = (self.selected_index + 1) % len(self.menu_options)
    
    def select_current(self) -> MenuOption:
        """Выбирает текущую опцию."""
        return self.menu_options[self.selected_index]["action"]
    
    def handle_input(self) -> MenuOption:
        """Обрабатывает ввод пользователя."""
        while True:
            self.display()
            
            key = input_handler.get_key().lower()
            
            if key in ['w', 'up']:
                self.move_up()
            elif key in ['s', 'down']:
                self.move_down()
            elif key == 'enter':
                choice = self.select_current()
                if choice in self.callbacks:
                    self.callbacks[choice]()
                return choice
            elif key == 'q':
                return MenuOption.EXIT


def show_main_menu() -> MenuOption:
    """Показывает главное меню и возвращает выбор."""
    menu = MainMenu()
    
    # Устанавливаем простые заглушки для callbacks
    menu.set_callback(MenuOption.NEW_GAME, lambda: None)
    menu.set_callback(MenuOption.LOAD_GAME, lambda: None)
    menu.set_callback(MenuOption.SETTINGS, lambda: None)
    menu.set_callback(MenuOption.EXIT, lambda: None)
    
    return menu.handle_input()
