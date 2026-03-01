"""Тесты Use Cases после рефакторинга."""

import sys
from unittest.mock import Mock

# Добавляем src в Python path для тестов
sys.path.insert(0, 'src')

from interfaces.user_interface import UserInterface
from use_cases.game import GameUseCase


def test_game_use_case_menu_integration():
    """Тест интеграции меню в GameUseCase (KISS)."""
    mock_ui = Mock(spec=UserInterface)
    mock_ui.get_int_input.return_value = 5  # EXIT

    use_case = GameUseCase(mock_ui)
    result = use_case.show_and_handle_menu()

    # Проверяем, что меню было показано
    mock_ui.clear.assert_called()
    mock_ui.print_title.assert_called_with("D&D Text MUD")
    mock_ui.print_separator.assert_called()
    mock_ui.print_menu_item.assert_called_with(5, "Выход")

    # Проверяем, что выход обработан правильно
    mock_ui.print_success.assert_called_with("Спасибо за игру!")
    assert result is False


def test_game_use_case_new_game():
    """Тест обработки новой игры."""
    mock_ui = Mock(spec=UserInterface)
    mock_ui.get_int_input.return_value = 1  # NEW_GAME
    mock_ui.get_input.return_value = "Тестовый персонаж"

    use_case = GameUseCase(mock_ui)
    result = use_case.show_and_handle_menu()

    # Проверяем, что персонаж создан
    mock_ui.print_success.assert_called_with("Персонаж Тестовый персонаж создан!")
    assert result is True
    assert use_case.has_active_session()


def test_game_use_case_invalid_choice():
    """Тест обработки неверного выбора."""
    mock_ui = Mock(spec=UserInterface)
    mock_ui.get_int_input.return_value = 99  # Неверный выбор

    use_case = GameUseCase(mock_ui)
    result = use_case.show_and_handle_menu()

    # Проверяем обработку ошибки
    mock_ui.print_error.assert_called_with("Неверный выбор. Попробуйте снова.")
    assert result is True


def test_game_use_case_load_game():
    """Тест обработки загрузки игры."""
    mock_ui = Mock(spec=UserInterface)
    mock_ui.get_int_input.return_value = 2  # LOAD_GAME

    use_case = GameUseCase(mock_ui)
    result = use_case.show_and_handle_menu()

    # Проверяем сообщение о недоступности
    mock_ui.print_info.assert_called_with("Функция пока недоступна.")
    assert result is True


def test_game_use_case_session_management():
    """Тест управления сессиями."""
    mock_ui = Mock(spec=UserInterface)

    use_case = GameUseCase(mock_ui)

    # Изначально нет активной сессии
    assert not use_case.has_active_session()
    assert use_case.get_current_session() is None

    # После создания персонажа есть сессия
    mock_ui.get_int_input.return_value = 1  # NEW_GAME
    mock_ui.get_input.return_value = "Тест"

    use_case.show_and_handle_menu()

    assert use_case.has_active_session()
    assert use_case.get_current_session() is not None
    assert use_case.get_current_session().player.name == "Тест"
