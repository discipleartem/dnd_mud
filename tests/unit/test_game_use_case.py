"""Тесты для Use Case игры."""

from unittest.mock import Mock

from core.constants import NOT_AVAILABLE, THANKS_FOR_PLAYING
from src.entities.character import Character
from src.use_cases.game import GameUseCase


class TestGameUseCase:
    """Тесты для GameUseCase."""

    def test_init(self) -> None:
        """Тест инициализации."""
        ui = Mock()
        game_use_case = GameUseCase(ui)

        assert game_use_case.ui == ui
        assert game_use_case._character is None

    def test_has_active_character(self) -> None:
        """Тест проверки активного персонажа."""
        ui = Mock()
        game_use_case = GameUseCase(ui)

        assert game_use_case.has_active_character() is False

        game_use_case._character = Character(name="Тест")
        assert game_use_case.has_active_character() is True

    def test_get_current_character(self) -> None:
        """Тест получения текущего персонажа."""
        ui = Mock()
        game_use_case = GameUseCase(ui)

        assert game_use_case.get_current_character() is None

        character = Character(name="Тест")
        game_use_case._character = character
        assert game_use_case.get_current_character() is character

    def test_create_new_character_success(self) -> None:
        """Тест успешного создания персонажа."""
        ui = Mock()
        ui.get_input.return_value = "Тестовый персонаж"

        game_use_case = GameUseCase(ui)
        game_use_case._create_new_character()

        assert game_use_case._character is not None
        assert game_use_case._character.name == "Тестовый персонаж"
        ui.print_success.assert_called_once()
        ui.print_info.assert_called()

    def test_create_new_character_empty_name(self) -> None:
        """Тест создания персонажа с пустым именем."""
        ui = Mock()
        ui.get_input.return_value = ""

        game_use_case = GameUseCase(ui)
        game_use_case._create_new_character()

        assert game_use_case._character is None
        ui.print_error.assert_called_once()

    def test_handle_menu_choice_exit(self) -> None:
        """Тест выбора выхода из меню."""
        ui = Mock()
        game_use_case = GameUseCase(ui)

        result = game_use_case._handle_menu_choice(4)  # Выход

        assert result is False
        ui.print_success.assert_called_once_with(THANKS_FOR_PLAYING)

    def test_handle_menu_choice_new_game(self) -> None:
        """Тест выбора новой игры."""
        ui = Mock()
        ui.get_input.return_value = "Тест"

        game_use_case = GameUseCase(ui)
        result = game_use_case._handle_menu_choice(1)  # Новая игра

        assert result is True
        assert game_use_case._character is not None

    def test_handle_menu_choice_not_available(self) -> None:
        """Тест выбора недоступной функции."""
        ui = Mock()

        game_use_case = GameUseCase(ui)
        result = game_use_case._handle_menu_choice(2)  # Загрузить игру

        assert result is True
        ui.show_message_and_wait.assert_called_once_with(NOT_AVAILABLE)
