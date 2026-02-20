"""
Тесты для main.py - точки входа в приложение.

Тестируем:
- Запуск приложения
- Обработку исключений
- Настройку логирования
- Главное меню и его опции
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
import logging

# Добавляем корень проекта в Python path для импортов
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# flake8: noqa: E402  # Импорты после настройки пути для тестов
from main import (
    setup_logging,
    show_splash_screen,
    handle_new_game,
    handle_load_game,
    handle_settings,
    main,
)
from src.infrastructure.ui.menus.main_menu import MenuOption

pytestmark = pytest.mark.unit


def create_mock_character(name: str = "Тестовый персонаж"):
    """Создает правильный мок персонажа с всеми необходимыми атрибутами."""
    mock_character = Mock()
    mock_character.name = name

    # Создаем моки для race и character_class
    mock_race = Mock()
    mock_race.name = "Человек"
    mock_character.race = mock_race

    mock_char_class = Mock()
    mock_char_class.name = "Воин"
    mock_character.character_class = mock_char_class

    mock_character.level = 1
    mock_character.hp_current = 10
    mock_character.hp_max = 10
    mock_character.ac = 12
    mock_character.get_all_modifiers.return_value = {
        "strength": 1,
        "dexterity": 0,
        "constitution": 1,
        "intelligence": 0,
        "wisdom": 0,
        "charisma": 0,
    }

    # Добавляем атрибуты характеристик
    attributes = [
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    ]
    for attr in attributes:
        mock_attr = Mock()
        mock_attr.value = 12 if attr == "strength" else 10
        setattr(mock_character, attr, mock_attr)

    return mock_character


class TestLoggingSetup:
    """Тесты настройки логирования."""

    def test_setup_logging_configures_basic_logging(self):
        """Тестирует базовую настройку логирования."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging()

            # Проверяем, что basicConfig был вызван
            mock_config.assert_called_once()
            call_args = mock_config.call_args

            # Проверяем основные параметры
            assert call_args.kwargs["level"] == logging.INFO
            assert "format" in call_args.kwargs
            assert "handlers" in call_args.kwargs
            assert len(call_args.kwargs["handlers"]) == 2

    def test_setup_logging_creates_file_handler(self):
        """Тестирует создание файлового обработчика."""
        with patch("logging.FileHandler") as mock_file_handler:
            setup_logging()
            mock_file_handler.assert_called_once_with("dnd_mud.log", encoding="utf-8")


class TestSplashScreen:
    """Тесты заставки игры."""

    @patch("builtins.input")
    @patch("main.renderer")
    def test_show_splash_screen_displays_content(self, mock_renderer, mock_input):
        """Тестирует отображение заставки."""
        mock_input.return_value = ""
        mock_renderer.get_input.return_value = ""

        show_splash_screen()

        mock_renderer.clear_screen.assert_called_once()
        # Проверяем, что get_input был вызван для ожидания нажатия Enter
        mock_renderer.get_input.assert_called_once_with()


class TestMainMenuHandlers:
    """Тесты обработчиков главного меню."""

    @patch("builtins.input")
    @patch("main.renderer")  # Патчим renderer из main
    @patch("src.infrastructure.ui.input_handler.input_handler")
    @patch("main.CharacterManager")
    def test_handle_new_game_success(
        self, mock_manager_class, mock_input, mock_renderer, mock_builtin_input
    ):
        """Тестирует успешную обработку новой игры."""
        # Настройка моков
        mock_builtin_input.return_value = ""
        mock_input.wait_for_enter.return_value = None

        mock_character = create_mock_character()

        mock_creation_controller = Mock()
        mock_creation_controller.create_character.return_value = mock_character

        mock_manager_instance = Mock()
        mock_manager_instance.save_character.return_value = True

        # Патчим get_instance чтобы возвращал наш мок
        mock_manager_class.get_instance.return_value = mock_manager_instance

        # Отключаем проверку сериализации для save_character
        mock_manager_instance.save_character = Mock(return_value=True)

        with patch(
            "main.CharacterCreationController",
            return_value=mock_creation_controller,
        ):
            handle_new_game()

        # Проверяем, что персонаж был создан и сохранен
        mock_creation_controller.create_character.assert_called_once()
        mock_manager_instance.save_character.assert_called_once()
        mock_renderer.show_success.assert_called_once()

    @patch("builtins.input")
    @patch("main.renderer")  # Патчим renderer из main
    @patch("src.infrastructure.ui.input_handler.input_handler")
    @patch("main.CharacterManager")
    def test_handle_new_game_cancellation(
        self, mock_manager_class, mock_input, mock_renderer, mock_builtin_input
    ):
        """Тестирует отмену новой игры."""
        # Настройка моков
        mock_builtin_input.return_value = ""
        mock_input.wait_for_enter.return_value = None

        mock_creation_controller = Mock()
        mock_creation_controller.create_character.return_value = None  # Отмена

        mock_manager_instance = Mock()
        mock_manager_class.get_instance.return_value = mock_manager_instance

        with patch(
            "main.CharacterCreationController",
            return_value=mock_creation_controller,
        ):
            handle_new_game()

        # Проверяем, что персонаж не был сохранен
        mock_creation_controller.create_character.assert_called_once()
        mock_manager_instance.save_character.assert_not_called()
        mock_renderer.show_info.assert_called_once()

    def test_handle_load_game_with_characters(
        self,
    ):
        """Тестирует загрузку игры с сохраненными персонажами."""
        from src.adapters.repositories.character_repository import CharacterManager

        # Настройка моков
        mock_characters = ["character1.json", "character2.json"]
        mock_manager_instance = Mock()
        mock_manager_instance.list_characters.return_value = mock_characters
        mock_manager_instance.get_character_info.return_value = {
            "name": "Тестовый персонаж",
            "race": "Человек",
            "class": "Воин",
            "level": 1,
        }

        # Создаем mock для загруженного персонажа с минимальными атрибутами
        mock_loaded_character = Mock()
        mock_loaded_character.name = "Тестовый персонаж"

        # Создаем моки для race и character_class
        mock_race = Mock()
        mock_race.name = "Человек"
        mock_loaded_character.race = mock_race

        mock_char_class = Mock()
        mock_char_class.name = "Воин"
        mock_loaded_character.character_class = mock_char_class

        mock_loaded_character.level = 1
        mock_loaded_character.hp_current = 10
        mock_loaded_character.hp_max = 10
        mock_loaded_character.ac = 12
        mock_loaded_character.gold = 100

        # Создаем моки для атрибутов персонажа
        mock_strength = Mock()
        mock_strength.value = 15
        mock_dexterity = Mock()
        mock_dexterity.value = 14
        mock_constitution = Mock()
        mock_constitution.value = 13
        mock_intelligence = Mock()
        mock_intelligence.value = 12
        mock_wisdom = Mock()
        mock_wisdom.value = 10
        mock_charisma = Mock()
        mock_charisma.value = 8

        # Присваиваем атрибуты персонажу
        mock_loaded_character.strength = mock_strength
        mock_loaded_character.dexterity = mock_dexterity
        mock_loaded_character.constitution = mock_constitution
        mock_loaded_character.intelligence = mock_intelligence
        mock_loaded_character.wisdom = mock_wisdom
        mock_loaded_character.charisma = mock_charisma

        # Возвращаем полный словарь модификаторов со всеми нужными ключами
        modifiers_dict = {
            "strength": 2,
            "dexterity": 2,
            "constitution": 1,
            "intelligence": 1,
            "wisdom": 0,
            "charisma": -1,
        }
        mock_loaded_character.get_all_modifiers.return_value = modifiers_dict

        mock_manager_instance.load_character.return_value = mock_loaded_character
        mock_manager_instance.load_character.side_effect = lambda filename: (
            mock_loaded_character
        )

        # Создаем моки для renderer и input_handler
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.get_int.return_value = 1
        mock_input.wait_for_enter.return_value = None

        # Патчим все зависимости одновременно
        with patch.object(
            CharacterManager, "get_instance", return_value=mock_manager_instance
        ):
            with patch("main.renderer", mock_renderer):
                with patch("main.input_handler", mock_input):
                    with patch("builtins.print"):
                        with patch("builtins.input", return_value=""):
                            handle_load_game()

        # Проверяем вызовы
        mock_manager_instance.list_characters.assert_called_once()
        mock_manager_instance.load_character.assert_called_once_with("character1.json")
        mock_renderer.show_success.assert_called_once()

    def test_handle_load_game_no_characters(
        self,
    ):
        """Тестирует загрузку игры без сохраненных персонажей."""
        from src.adapters.repositories.character_repository import CharacterManager

        mock_manager_instance = Mock()
        mock_manager_instance.list_characters.return_value = []
        mock_manager_instance.get_character_info.return_value = None

        # Создаем моки для renderer и input_handler
        mock_renderer = Mock()
        mock_input = Mock()
        mock_input.wait_for_enter.return_value = None

        with patch.object(
            CharacterManager, "get_instance", return_value=mock_manager_instance
        ):
            with patch("main.renderer", mock_renderer):
                with patch("main.input_handler", mock_input):
                    with patch("builtins.print"):
                        with patch("builtins.input", return_value=""):
                            handle_load_game()

        # Проверяем вызовы
        mock_manager_instance.list_characters.assert_called_once()
        mock_renderer.show_info.assert_called_once_with(
            "Сохраненные персонажи не найдены"
        )
        mock_input.wait_for_enter.assert_called_once()

    def test_handle_settings(self):
        """Тестирует обработку настроек."""
        # Создаем моки для renderer и input_handler
        mock_renderer = Mock()
        mock_renderer.get_input.return_value = ""
        mock_input = Mock()

        with patch("main.renderer", mock_renderer):
            with patch("main.input_handler", mock_input):
                with patch("builtins.print"):
                    with patch("builtins.input", return_value=""):
                        handle_settings()

        # В handle_settings show_info вызывается дважды
        assert mock_renderer.show_info.call_count == 2
        mock_renderer.show_info.assert_any_call("Открытие настроек...")
        mock_renderer.show_info.assert_any_call(
            "Функция настроек будет реализована в следующей версии."
        )
        mock_renderer.get_input.assert_called_once()


class TestMainFunction:
    """Тесты основной функции приложения."""

    @patch("main.handle_settings")
    @patch("main.handle_load_game")
    @patch("main.handle_new_game")
    @patch("main.show_main_menu")
    @patch("main.show_splash_screen")
    @patch("main.setup_logging")
    def test_main_normal_exit(
        self,
        mock_setup,
        mock_splash,
        mock_menu,
        mock_new_game,
        mock_load_game,
        mock_settings,
    ):
        """Тестирует нормальный выход из программы."""
        mock_menu.return_value = MenuOption.EXIT

        result = main()

        assert result == 0
        mock_setup.assert_called_once()
        mock_splash.assert_called_once()
        mock_menu.assert_called_once()

    @patch("main.handle_settings")
    @patch("main.handle_load_game")
    @patch("main.handle_new_game")
    @patch("main.show_main_menu")
    @patch("main.show_splash_screen")
    @patch("main.setup_logging")
    def test_main_new_game_flow(
        self,
        mock_setup,
        mock_splash,
        mock_menu,
        mock_new_game,
        mock_load_game,
        mock_settings,
    ):
        """Тестирует поток новой игры."""
        # Сначала выбираем новую игру, потом выход
        mock_menu.side_effect = [MenuOption.NEW_GAME, MenuOption.EXIT]

        result = main()

        assert result == 0
        mock_new_game.assert_called_once()
        assert mock_menu.call_count == 2

    @patch("main.handle_settings")
    @patch("main.handle_load_game")
    @patch("main.handle_new_game")
    @patch("main.show_main_menu")
    @patch("main.show_splash_screen")
    @patch("main.setup_logging")
    def test_main_keyboard_interrupt(
        self,
        mock_setup,
        mock_splash,
        mock_menu,
        mock_new_game,
        mock_load_game,
        mock_settings,
    ):
        """Тестирует обработку KeyboardInterrupt."""
        mock_menu.side_effect = [
            KeyboardInterrupt(),  # Первое прерывание
            MenuOption.EXIT,  # Затем выход
        ]

        with patch("builtins.input", return_value="д"):
            result = main()

        assert result == 0

    @patch("main.setup_logging")
    @patch("logging.critical")
    def test_main_critical_error(self, mock_logging_critical, mock_setup):
        """Тестирует обработку критической ошибки."""
        mock_setup.side_effect = Exception("Критическая ошибка")

        with patch("builtins.print") as mock_print:
            result = main()

        assert result == 1
        # Проверяем, что print был вызван с сообщением об ошибке
        mock_print.assert_called_with(
            "Критическая ошибка при запуске игры: Критическая ошибка"
        )
        # Проверяем, что критический лог был записан
        mock_logging_critical.assert_called_once()

    @patch("main.handle_settings")
    @patch("main.handle_load_game")
    @patch("main.handle_new_game")
    @patch("main.show_main_menu")
    @patch("main.show_splash_screen")
    @patch("main.setup_logging")
    def test_main_menu_exception_handling(
        self,
        mock_setup,
        mock_splash,
        mock_menu,
        mock_new_game,
        mock_load_game,
        mock_settings,
    ):
        """Тестирует обработку исключений в меню."""
        mock_menu.side_effect = [Exception("Ошибка меню"), MenuOption.EXIT]

        # Создаем мок renderer с правильным поведением get_input
        mock_renderer = Mock()
        mock_renderer.get_input.side_effect = ["", ""]  # Два вызова get_input

        with patch("main.renderer", mock_renderer):
            with patch("main.input_handler", Mock()):
                with patch("builtins.print"):
                    with patch("builtins.input", return_value=""):
                        result = main()

        assert result == 0
        mock_renderer.show_error.assert_called_once()


class TestIntegration:
    """Интеграционные тесты."""

    @patch("main.show_splash_screen")
    @patch("main.setup_logging")
    def test_full_menu_navigation(self, mock_setup, mock_splash):
        """Тестирует полную навигацию по меню."""
        with patch("src.infrastructure.ui.renderer.renderer") as _mock_renderer:
            with patch(
                "src.infrastructure.ui.input_handler.input_handler"
            ) as _mock_input:
                # Мокаем show_main_menu для возврата разных опций
                with patch("main.show_main_menu") as mock_menu:
                    mock_menu.side_effect = [
                        MenuOption.SETTINGS,
                        MenuOption.LOAD_GAME,
                        MenuOption.NEW_GAME,
                        MenuOption.EXIT,
                    ]

                    with (
                        patch("main.handle_settings"),
                        patch("main.handle_load_game"),
                        patch("main.handle_new_game"),
                    ):
                        result = main()

                        assert result == 0
                        assert mock_menu.call_count == 4


if __name__ == "__main__":
    pytest.main([__file__])
