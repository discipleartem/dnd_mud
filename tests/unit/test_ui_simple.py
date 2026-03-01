"""Упрощенные тесты UI без colorama зависимостей."""

import pytest
from unittest.mock import Mock, patch

# Тестируем только базовые функции без colorama
import sys
import io


def test_console_basic_functionality():
    """Тест базовой функциональности консоли."""
    from ui.console import Console
    
    # Перенаправляем вывод в строковый буфер
    captured_output = io.StringIO()
    console = Console()
    
    # Тест очистки (не должна вызывать ошибок)
    console.clear()
    
    # Тест печати без colorama - просто проверяем, что метод вызывается
    console.print_info("Тестовое сообщение")
    
    # Проверяем, что вывод содержит сообщение
    output = captured_output.getvalue()
    # Простая проверка наличия текста
    assert "Тестовое сообщение" in output


def test_get_int_input_basic():
    """Тест базового числового ввода."""
    from ui.console import Console
    
    # Мокируем ввод
    with patch('builtins.input', return_value="5"):
        console = Console()
        result = console.get_int_input("Выбор: ", 1, 10)
        
        assert result == 5


def test_get_int_input_with_retry():
    """Тест числового ввода с повторной попыткой."""
    from ui.console import Console
    
    # Мокируем ввод: сначала ошибка, потом успех
    inputs = ["abc", "5"]
    input_iter = iter(inputs)
    
    with patch('builtins.input', side_effect=lambda x: next(input_iter)):
        console = Console()
        result = console.get_int_input("Выбор: ", 1, 10)
        
        # Должен вернуть второе значение
        assert result == 5


class TestScreensWithoutColorama:
    """Тесты экранов без colorama."""
    
    def test_welcome_screen_mock(self):
        """Тест экрана приветствия с моками."""
        from ui.screens import WelcomeScreen
        
        mock_console = Mock()
        screen = WelcomeScreen(mock_console)
        
        # Проверяем, что экран можно создать
        assert screen.console == mock_console
    
    def test_main_menu_screen_mock(self):
        """Тест главного меню с моками."""
        from ui.screens import MainMenuScreen
        
        mock_console = Mock()
        menu = MainMenuScreen(mock_console)
        
        # Проверяем, что меню можно создать
        assert menu.console == mock_console