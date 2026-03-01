"""Тесты Use Cases после рефакторинга."""

import pytest
import sys
from unittest.mock import Mock, patch

# Добавляем src в Python path для тестов
sys.path.insert(0, 'src')

from use_cases.menu_navigation import HandleMenuChoiceUseCase, ShowMenuUseCase
from ui.screen_factory import DefaultScreenFactory
from interfaces.user_interface import UserInterface


def test_show_menu_use_case():
    """Тест ShowMenuUseCase с dependency injection."""
    mock_ui = Mock(spec=UserInterface)
    mock_factory = Mock(spec=DefaultScreenFactory)
    mock_menu = Mock()
    mock_menu.show.return_value = 3
    
    mock_factory.create_main_menu.return_value = mock_menu
    
    use_case = ShowMenuUseCase(mock_ui, mock_factory)
    result = use_case.execute()
    
    mock_factory.create_main_menu.assert_called_once_with(mock_ui)
    mock_menu.show.assert_called_once()
    assert result == 3


def test_handle_menu_choice_exit():
    """Тест обработки выбора выхода."""
    mock_ui = Mock(spec=UserInterface)
    
    use_case = HandleMenuChoiceUseCase(mock_ui)
    result = use_case.execute(5)  # EXIT = 5
    
    mock_ui.print_success.assert_called_once_with("Спасибо за игру!")
    assert result is False


def test_handle_menu_choice_valid_option():
    """Тест обработки допустимой опции."""
    mock_ui = Mock(spec=UserInterface)
    
    use_case = HandleMenuChoiceUseCase(mock_ui)
    result = use_case.execute(1)  # NEW_GAME = 1
    
    mock_ui.print_info.assert_called_once_with("Выберите опцию:")
    assert result is True


def test_handle_menu_choice_invalid_option():
    """Тест обработки недопустимой опции."""
    mock_ui = Mock(spec=UserInterface)
    mock_ui.get_input.return_value = ""
    
    use_case = HandleMenuChoiceUseCase(mock_ui)
    result = use_case.execute(99)  # Недопустимый выбор
    
    mock_ui.print_info.assert_called_once_with("Неверный выбор. Попробуйте снова.")
    mock_ui.get_input.assert_called_once_with("нажмите Enter для продолжения...")
    assert result is True


def test_get_choice_message():
    """Тест получения сообщения для выбора."""
    mock_ui = Mock(spec=UserInterface)
    
    use_case = HandleMenuChoiceUseCase(mock_ui)
    
    # Тест существующего выбора
    message = use_case._get_choice_message(2)  # LOAD_GAME = 2
    assert message == "Функция загрузки пока недоступна."
    
    # Тест несуществующего выбора
    message = use_case._get_choice_message(99)
    assert message == "Неверный выбор. Попробуйте снова."


def test_get_valid_choices():
    """Тест получения списка допустимых выборов."""
    mock_ui = Mock(spec=UserInterface)
    
    use_case = HandleMenuChoiceUseCase(mock_ui)
    choices = use_case._get_valid_choices()
    
    expected_choices = [1, 2, 3, 4]  # NEW_GAME, LOAD_GAME, SETTINGS, MODS
    assert choices == expected_choices
