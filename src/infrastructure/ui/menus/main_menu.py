"""Модуль главного меню D&D MUD."""

from enum import Enum
from typing import Callable, Dict, Union

from ..renderer import Renderer
from ..input_handler import InputHandler


class MenuOption(Enum):
    """Опции главного меню."""

    NEW_GAME = "new_game"
    LOAD_GAME = "load_game"
    SETTINGS = "settings"
    EXIT = "exit"


class MainMenu:
    """Простое главное меню игры."""

    def __init__(self, renderer: Renderer, input_handler: InputHandler) -> None:
        """Инициализация меню."""
        self.renderer = renderer
        self.input_handler = input_handler
        self.selected_index = 0
        self.menu_options = [
            {"text": "Новая игра", "action": MenuOption.NEW_GAME},
            {"text": "Загрузить игру", "action": MenuOption.LOAD_GAME},
            {"text": "Настройки", "action": MenuOption.SETTINGS},
            {"text": "Выход", "action": MenuOption.EXIT},
        ]
        self.callbacks: Dict[MenuOption, Callable[..., Union[str, int, None]]] = {}

    def set_callback(
        self, option: MenuOption, callback: Callable[..., Union[str, int, None]]
    ) -> None:
        """Устанавливает callback функцию для опции меню."""
        self.callbacks[option] = callback

    def display(self) -> None:
        """Отображает меню."""
        self.renderer.clear_screen()
        self.renderer.render_title("D&D MUD - Главное меню")

        print("\n" + "=" * 50)
        for i, option in enumerate(self.menu_options):
            marker = "►" if i == self.selected_index else " "
            print(f"{marker} {i + 1}. {option['text']}")
        print("=" * 50)

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
        action = self.menu_options[self.selected_index]["action"]
        # Явное преобразование в MenuOption
        if isinstance(action, str):
            try:
                return MenuOption(action)
            except ValueError:
                # Если значение не соответствует enum, возвращаем по умолчанию
                return MenuOption.EXIT
        # Если action уже MenuOption, возвращаем как есть
        if isinstance(action, MenuOption):
            return action
        # В крайнем случае возвращаем EXIT
        return MenuOption.EXIT

    def handle_input(self) -> MenuOption:
        """Обрабатывает ввод пользователя."""
        while True:
            self.display()

            key = input().lower()

            if key in ["w", "up"]:
                self.move_up()
            elif key in ["s", "down"]:
                self.move_down()
            elif key == "enter":
                choice = self.select_current()
                if choice in self.callbacks:
                    self.callbacks[choice]()
                return choice
            elif key == "q":
                return MenuOption.EXIT


def show_new_game_menu(renderer: Renderer, input_handler: InputHandler) -> None:
    """Показывает меню новой игры."""
    menu = MainMenu(renderer, input_handler)
    menu.set_callback(MenuOption.NEW_GAME, lambda: None)
    menu.display()
    input_handler.wait_for_enter()


def show_load_game_menu(renderer: Renderer, input_handler: InputHandler) -> None:
    """Показывает меню загрузки игры."""
    menu = MainMenu(renderer, input_handler)
    menu.set_callback(MenuOption.LOAD_GAME, lambda: None)
    menu.display()
    input_handler.wait_for_enter()


def show_settings_menu(renderer: Renderer, input_handler: InputHandler) -> None:
    """Показывает меню настроек."""
    from .settings import SettingsController

    settings_controller = SettingsController(input_handler, renderer)
    settings_controller.show_settings()


def show_main_menu(renderer: Renderer, input_handler: InputHandler) -> MenuOption:
    """Показывает главное меню и возвращает выбор."""
    menu = MainMenu(renderer, input_handler)

    # Устанавливаем простые заглушки для callbacks
    menu.set_callback(MenuOption.NEW_GAME, lambda: None)
    menu.set_callback(MenuOption.LOAD_GAME, lambda: None)
    menu.set_callback(MenuOption.SETTINGS, lambda: None)
    menu.set_callback(MenuOption.EXIT, lambda: None)

    return menu.handle_input()


class NewGameMenu:
    """Меню новой игры."""

    def __init__(self, renderer: Renderer, input_handler: InputHandler) -> None:
        """Инициализирует меню новой игры."""
        self.renderer = renderer
        self.input_handler = input_handler

    def show(self) -> None:
        """Показывает меню новой игры."""
        self.renderer.clear_screen()
        self.renderer.render_title("Новая игра")
        print("\nСоздание нового персонажа...")
        print("\nНажмите Enter для продолжения...")
        self.input_handler.wait_for_enter()
