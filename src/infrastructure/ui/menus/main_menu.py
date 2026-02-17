"""
Модуль главного меню D&D MUD.

Реализует главное меню игры с выбором опций.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Callable, Dict, List
from enum import Enum

# Добавляем src в Python path для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.ui.renderer import renderer
from src.infrastructure.ui.input_handler import input_handler
from src.infrastructure.ui.menus.character_creation import CharacterCreationController
from src.infrastructure.ui.menus.settings import SettingsController


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
        max_attempts = 20  # Ограничиваем количество показов меню
        attempts = 0

        try:
            while attempts < max_attempts:
                attempts += 1
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

            # Если превысили количество попыток, выходим
            return MenuOption.EXIT

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
        settings_controller = SettingsController(input_handler, renderer)
        settings_controller.show_settings()


class NewGameMenu:
    """Класс меню создания новой игры."""

    def __init__(self) -> None:
        """Инициализирует меню новой игры."""
        self.controller = CharacterCreationController(input_handler, renderer)

    def show(self) -> None:
        """Отображает меню создания новой игры."""
        renderer.clear_screen()
        renderer.show_title("Новая игра", "Создание персонажа")

        print("\nВыберите способ создания персонажа:")
        print("1. Полное создание персонажа (пошагово)")
        print("2. Быстрое создание (с настройками по умолчанию)")
        print("3. Создать персонажа 1 уровня (по умолчанию)")
        print("4. Вернуться в главное меню")

        choice = input_handler.get_menu_choice(4)

        if choice == 1:
            self._create_full_character()
        elif choice == 2:
            self._create_quick_character()
        elif choice == 3:
            self._create_default_character()
        # choice == 4 - просто выходим из меню

    def _create_full_character(self) -> None:
        """Создает персонажа через полное меню."""
        try:
            character = self.controller.create_character()
            if character:
                renderer.show_success(f"Персонаж {character.name} успешно создан!")
                renderer.get_input("Нажмите Enter для продолжения...")
        except KeyboardInterrupt:
            renderer.show_info("Создание персонажа отменено")

    def _create_quick_character(self) -> None:
        """Создает персонажа быстро с подтверждением имени."""
        renderer.clear_screen()
        renderer.show_title("Быстрое создание персонажа")

        # Получаем имя с подтверждением
        while True:
            name = input_handler.get_string(
                "Введите имя персонажа: ", allow_empty=False
            )

            renderer.clear_screen()
            renderer.show_title("Подтверждение имени")
            print(f"\nВы ввели имя: {name}")
            print("Создать персонажа с этим именем?")
            
            print("\n1. Да, создать")
            print("2. Нет, ввести другое имя")
            print("3. Отменить")
            
            confirm_choice = input_handler.get_menu_choice(3)
            
            if confirm_choice == 1:
                try:
                    character = self.controller.create_quick_character(name)
                    renderer.show_success(f"Персонаж {character.name} ({character.level} уровень) успешно создан!")
                    renderer.get_input("Нажмите Enter для продолжения...")
                except Exception as e:
                    renderer.show_error(f"Ошибка при создании персонажа: {e}")
                    renderer.get_input("Нажмите Enter для продолжения...")
                break
            elif confirm_choice == 2:
                continue
            else:
                break

    def _create_default_character(self) -> None:
        """Создает персонажа по умолчанию с 1 уровнем."""
        try:
            character = self.controller.create_default_character()
            renderer.show_success(f"Персонаж {character.name} (1 уровень) успешно создан!")
            renderer.get_input("Нажмите Enter для продолжения...")
        except Exception as e:
            renderer.show_error(f"Ошибка при создании персонажа: {e}")
            renderer.get_input("Нажмите Enter для продолжения...")


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
