"""Тесты для экранов после рефакторинга."""

import pytest
import sys
from unittest.mock import patch

# Добавляем src в Python path для тестов
sys.path.insert(0, 'src')

from ui.screens import WelcomeScreen, MainMenuScreen
from interfaces.user_interface import UserInterface


class MockUI(UserInterface):
    """Mock реализация UserInterface для тестов."""
    
    def __init__(self):
        self.clear_calls = 0
        self.print_calls = []
        self.input_calls = []
        self.int_input_calls = []
    
    def clear(self) -> None:
        self.clear_calls += 1
    
    def print_info(self, text: str) -> None:
        self.print_calls.append(("info", text))
    
    def print_error(self, text: str) -> None:
        self.print_calls.append(("error", text))
    
    def print_success(self, text: str) -> None:
        self.print_calls.append(("success", text))
    
    def print_title(self, text: str) -> None:
        self.print_calls.append(("title", text))
    
    def print_menu_item(self, number: int, text: str) -> None:
        self.print_calls.append(("menu_item", f"{number}. {text}"))
    
    def print_separator(self) -> None:
        self.print_calls.append(("separator", "=" * 50 + "="))
    
    def get_input(self, prompt: str = "") -> str:
        self.input_calls.append(("input", prompt))
        return self.input_responses.pop(0) if self.input_responses else ""
    
    def get_int_input(self, prompt: str = "", min_val: int | None = None,
                   max_val: int | None = None) -> int:
        self.int_input_calls.append(("int_input", prompt, min_val, max_val))
        return self.int_input_responses.pop(0) if self.int_input_responses else 1


def test_welcome_screen_show():
    """Тест отображения экрана приветствия."""
    mock_ui = MockUI()
    screen = WelcomeScreen(mock_ui)
    
    screen.show()
    
    # Проверяем, что clear был вызван
    assert mock_ui.clear_calls == 1
    
    # Проверяем, что title был напечатан
    title_calls = [call for call in mock_ui.print_calls if call[0] == "title"]
    assert len(title_calls) == 1
    assert "D&D TEXT MUD" in title_calls[0][1]
    
    # Проверяем, что separator был напечатан
    separator_calls = [call for call in mock_ui.print_calls if call[0] == "separator"]
    assert len(separator_calls) == 1


def test_main_menu_screen_show():
    """Тест отображения главного меню."""
    mock_ui = MockUI()
    mock_ui.int_input_responses = [3]  # Пользователь выбирает "Настройки"
    
    screen = MainMenuScreen(mock_ui)
    result = screen.show()
    
    # Проверяем результат
    assert result == 3
    
    # Проверяем, что clear был вызван
    assert mock_ui.clear_calls == 1
    
    # Проверяем, что title был напечатан
    title_calls = [call for call in mock_ui.print_calls if call[0] == "title"]
    assert len(title_calls) == 1
    assert "ГЛАВНОЕ МЕНЮ" in title_calls[0][1]
    
    # Проверяем, что все пункты меню были напечатаны
    menu_calls = [call for call in mock_ui.print_calls if call[0] == "menu_item"]
    assert len(menu_calls) == 5  # 5 пунктов меню
    
    # Проверяем, что separator был напечатан
    separator_calls = [call for call in mock_ui.print_calls if call[0] == "separator"]
    assert len(separator_calls) == 1
    
    # Проверяем, что get_int_input был вызван с правильными параметрами
    assert len(mock_ui.int_input_calls) == 1
    assert mock_ui.int_input_calls[0][0] == "Ваш выбор: "
    assert mock_ui.int_input_calls[0][1] == 1  # min_val
    assert mock_ui.int_input_calls[0][2] == 5  # max_val


def test_main_menu_screen_input_validation():
    """Тест валидации ввода в главном меню."""
    mock_ui = MockUI()
    
    # Тест невалидного ввода (меньше минимума)
    mock_ui.int_input_responses = [0, 1]  # Сначала 0 (невалидно), потом 1
    screen = MainMenuScreen(mock_ui)
    result = screen.show()
    
    # Проверяем, что был вызван get_int_input дважды
    assert len(mock_ui.int_input_calls) == 2
    
    # Результат должен быть 1 (валидный выбор)
    assert result == 1
