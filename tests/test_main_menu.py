"""
Тесты для главного меню игры.

Тестируем:
- Инициализацию меню
- Отображение опций
- Обработку выбора пользователя
- Callback функции
- Обработку исключений
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.menus.main_menu import (
    MainMenu,
    MenuOption,
    NewGameMenu,
    show_main_menu,
    show_new_game_menu,
    show_load_game_menu,
    show_settings_menu,
)

pytestmark = pytest.mark.unit


class TestMainMenu:
    """Тесты класса главного меню."""

    def test_main_menu_initialization(self):
        """Тестирует инициализацию главного меню."""
        menu = MainMenu()

        assert menu.selected_index == 0
        assert len(menu.menu_options) == 4
        assert menu.menu_options[0]["text"] == "Новая игра"
        assert menu.menu_options[0]["action"] == MenuOption.NEW_GAME
        assert menu.menu_options[3]["text"] == "Выход"
        assert menu.menu_options[3]["action"] == MenuOption.EXIT
        assert len(menu.callbacks) == 0

    def test_set_callback(self):
        """Тестирует установку callback функции."""
        menu = MainMenu()
        mock_callback = Mock()

        menu.set_callback(MenuOption.NEW_GAME, mock_callback)

        assert MenuOption.NEW_GAME in menu.callbacks
        assert menu.callbacks[MenuOption.NEW_GAME] == mock_callback

    def test_show_displays_menu_content(self):
        """Тестирует отображение меню."""
        menu = MainMenu()
        mock_renderer = Mock()
        
        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            menu.show()

        mock_renderer.show_title.assert_called_once_with(
            "Dungeons & Dragons MUD", "Текстовая ролевая игра"
        )
        mock_renderer.show_menu.assert_called_once_with(
            "Главное меню", menu.menu_options
        )

    def test_run_exit_option(self):
        """Тестирует выбор опции выхода."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_menu_choice.return_value = 4  # Выход

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value=""):
                    result = menu.run()

        assert result == MenuOption.EXIT
        assert menu.selected_index == 3  # Индекс опции выхода

    def test_run_new_game_with_callback(self):
        """Тестирует выбор новой игры с callback."""
        menu = MainMenu()
        mock_callback = Mock()
        menu.set_callback(MenuOption.NEW_GAME, mock_callback)
        
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_menu_choice.return_value = 1  # Новая игра

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value="1"):
                    result = menu.run()

        assert result == MenuOption.NEW_GAME
        mock_callback.assert_called_once()

    def test_run_load_game_without_callback(self):
        """Тестирует выбор загрузки игры без callback."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_menu_choice.return_value = 2  # Загрузить игру

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value="2"):
                    result = menu.run()

        assert result == MenuOption.LOAD_GAME

    def test_run_keyboard_interrupt(self):
        """Тестирует обработку KeyboardInterrupt."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_menu_choice.side_effect = KeyboardInterrupt()

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", side_effect=KeyboardInterrupt()):
                    result = menu.run()

        assert result == MenuOption.EXIT

    def test_run_general_exception(self):
        """Тестирует обработку общих исключений."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_menu_choice.side_effect = Exception("Тестовая ошибка")

        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", side_effect=Exception("Тестовая ошибка")):
                    result = menu.run()

        assert result == MenuOption.EXIT
        mock_renderer.show_error.assert_called_once()

    def test_show_load_game_menu(self):
        """Тестирует отображение меню загрузки игры."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value=""):
                    menu.show_load_game_menu()

        mock_renderer.show_info.assert_called_once_with(
            "Функция загрузки игры пока не реализована"
        )
        mock_renderer.get_input.assert_called_once_with(
            "Нажмите Enter для возврата в главное меню..."
        )

    def test_show_settings_menu(self):
        """Тестирует отображение меню настроек."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value=""):
                    menu.show_settings_menu()

        mock_renderer.show_info.assert_called_once_with(
            "Функция настроек пока не реализована"
        )
        mock_renderer.get_input.assert_called_once_with(
            "Нажмите Enter для возврата в главное меню..."
        )


class TestNewGameMenu:
    """Тесты меню новой игры."""

    def test_new_game_menu_show(self):
        """Тестирует отображение меню новой игры."""
        menu = NewGameMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value=""):
                    menu.show()

        mock_renderer.show_title.assert_called_once_with(
            "Создание персонажа", "Шаг за шагом создайте своего героя"
        )
        mock_renderer.show_info.assert_called_once_with(
            "Функция создания персонажа будет реализована в следующей версии"
        )
        mock_renderer.get_input.assert_called_once_with(
            "Нажмите Enter для возврата в главное меню..."
        )


class TestConvenienceFunctions:
    """Тесты удобных функций."""

    @patch("src.infrastructure.ui.menus.main_menu.MainMenu.run")
    def test_show_main_menu_function(self, mock_run):
        """Тестирует функцию show_main_menu."""
        mock_run.return_value = MenuOption.EXIT

        result = show_main_menu()

        assert result == MenuOption.EXIT
        mock_run.assert_called_once()

    @patch("src.infrastructure.ui.menus.main_menu.NewGameMenu.show")
    def test_show_new_game_menu_function(self, mock_show):
        """Тестирует функцию show_new_game_menu."""
        show_new_game_menu()
        mock_show.assert_called_once()

    @patch("src.infrastructure.ui.menus.main_menu.MainMenu.show_load_game_menu")
    def test_show_load_game_menu_function(self, mock_show_load):
        """Тестирует функцию show_load_game_menu."""
        mock_show_load.return_value = None

        result = show_load_game_menu()

        mock_show_load.assert_called_once()
        assert result is None

    @patch("src.infrastructure.ui.menus.main_menu.MainMenu.show_settings_menu")
    def test_show_settings_menu_function(self, mock_show_settings):
        """Тестирует функцию show_settings_menu."""
        show_settings_menu()
        mock_show_settings.assert_called_once()


class TestMenuOption:
    """Тесты enum опций меню."""

    def test_menu_option_values(self):
        """Тестирует значения опций меню."""
        assert MenuOption.NEW_GAME.value == "new_game"
        assert MenuOption.LOAD_GAME.value == "load_game"
        assert MenuOption.SETTINGS.value == "settings"
        assert MenuOption.EXIT.value == "exit"

    def test_menu_option_uniqueness(self):
        """Тестирует уникальность опций меню."""
        values = [option.value for option in MenuOption]
        assert len(values) == len(set(values))


class TestMenuIntegration:
    """Интеграционные тесты меню."""

    def test_full_menu_flow_with_callbacks(self):
        """Тестирует полный поток меню с callback функциями."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        # Настраиваем callback функции
        new_game_callback = Mock()
        load_game_callback = Mock()
        settings_callback = Mock()

        menu.set_callback(MenuOption.NEW_GAME, new_game_callback)
        menu.set_callback(MenuOption.LOAD_GAME, load_game_callback)
        menu.set_callback(MenuOption.SETTINGS, settings_callback)

        # Тестируем каждую опцию
        test_cases = [
            (1, MenuOption.NEW_GAME, new_game_callback),
            (2, MenuOption.LOAD_GAME, load_game_callback),
            (3, MenuOption.SETTINGS, settings_callback),
            (4, MenuOption.EXIT, None),
        ]

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                for choice, expected_result, expected_callback in test_cases:
                    mock_input.get_menu_choice.return_value = choice
                    with patch("builtins.input", return_value=str(choice)):
                        result = menu.run()

                    assert result == expected_result
                    if expected_callback:
                        expected_callback.assert_called_once()
                        expected_callback.reset_mock()


class TestMenuErrorHandling:
    """Тесты обработки ошибок в меню."""

    def test_callback_exception_handling(self):
        """Тестирует обработку исключений в callback функциях."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        # Создаем callback, который вызывает исключение
        def failing_callback():
            raise Exception("Ошибка в callback")

        menu.set_callback(MenuOption.NEW_GAME, failing_callback)
        mock_input.get_menu_choice.return_value = 1

        with patch("src.infrastructure.ui.menus.main_menu.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", return_value="1"):
                    # Должно обработать исключение и вернуть опцию меню
                    result = menu.run()

        assert result == MenuOption.EXIT

    def test_multiple_keyboard_interrupts(self):
        """Тестирует множественные KeyboardInterrupt."""
        menu = MainMenu()
        mock_renderer = Mock()
        mock_input = Mock()

        # Первый вызов вызывает исключение, второй возвращает выход
        mock_input.get_menu_choice.side_effect = [
            KeyboardInterrupt(),
            KeyboardInterrupt(),
        ]

        with patch("src.infrastructure.ui.renderer.renderer", mock_renderer):
            with patch("src.infrastructure.ui.input_handler.input_handler", mock_input):
                with patch("builtins.input", side_effect=KeyboardInterrupt()):
                    # Первый вызов должен вернуть EXIT
                    result1 = menu.run()
                    assert result1 == MenuOption.EXIT

                    # Второй вызов также должен вернуть EXIT
                    result2 = menu.run()
                    assert result2 == MenuOption.EXIT


if __name__ == "__main__":
    pytest.main([__file__])
