"""Unit тесты для UI компонентов."""

import pytest
from unittest.mock import Mock, patch

from ui.console import Console
from ui.screens import WelcomeScreen, MainMenuScreen


class TestConsole:
    """Тесты класса Console."""
    
    def test_clear(self):
        """Тест очистки экрана."""
        console = Console()
        # Просто проверяем, что метод не вызывает ошибок
        console.clear()
    
    def test_print_title(self, capsys):
        """Тест печати заголовка."""
        console = Console()
        console.print_title("Тест")
        captured = capsys.readouterr()
        assert "Тест" in captured
    
    def test_print_success(self, capsys):
        """Тест печати успешного сообщения."""
        console = Console()
        console.print_success("Успех")
        captured = capsys.readouterr()
        assert "Успех" in captured
    
    def test_print_error(self, capsys):
        """Тест печати ошибки."""
        console = Console()
        console.print_error("Ошибка")
        captured = capsys.readouterr()
        assert "Ошибка" in captured
    
    def test_print_menu_item(self, capsys):
        """Тест печати пункта меню."""
        console = Console()
        console.print_menu_item(1, "Пункт")
        captured = capsys.readouterr()
        assert "1. Пункт" in captured
    
    def test_get_input(self, monkeypatch):
        """Тест получения ввода."""
        console = Console()
        monkeypatch.setattr("builtins.input", lambda x: "test")
        result = console.get_input("Промпт: ")
        assert result == "test"
    
    def test_get_int_input_valid(self, monkeypatch):
        """Тест получения числового ввода - валидное значение."""
        console = Console()
        monkeypatch.setattr("builtins.input", lambda x: "5")
        result = console.get_int_input("Выбор: ", 1, 10)
        assert result == 5
    
    def test_get_int_input_invalid(self, monkeypatch):
        """Тест получения числового ввода - неверное значение."""
        console = Console()
        
        # Мокируем ввод: сначала "abc" (ошибка), потом "5" (успех)
        inputs = ["abc", "5"]
        input_iter = iter(inputs)
        monkeypatch.setattr("builtins.input", lambda x: next(input_iter))
        
        result = console.get_int_input("Выбор: ", 1, 10)
        
        # Должен вернуть 5 (второе значение)
        assert result == 5


class TestWelcomeScreen:
    """Тесты экрана приветствия."""
    
    def test_show(self, monkeypatch):
        """Тест показа экрана приветствия."""
        mock_console = Mock()
        screen = WelcomeScreen(mock_console)
        
        # Мокаем ввод пользователя
        monkeypatch.setattr("builtins.input", lambda x: "")
        
        screen.show()
        
        # Проверяем, что были вызваны методы консоли
        mock_console.clear.assert_called_once()
        mock_console.print_title.assert_called_once()
        mock_console.print_separator.assert_called_once()
        mock_console.print_info.assert_called_once()
        mock_console.get_input.assert_called_once()


class TestMainMenuScreen:
    """Тесты главного меню."""
    
    def test_show_valid_choice(self, monkeypatch):
        """Тест показа меню с валидным выбором."""
        mock_console = Mock()
        menu = MainMenuScreen(mock_console)
        
        # Мокаем ввод пользователя
        monkeypatch.setattr("builtins.input", lambda x: "3")
        
        result = menu.show()
        
        assert result == 3
        mock_console.clear.assert_called_once()
        mock_console.print_title.assert_called_once()
        mock_console.print_separator.assert_called_once()
        mock_console.get_int_input.assert_called_once_with("Ваш выбор: ", 1, 5)
    
    def test_show_invalid_choice(self, monkeypatch):
        """Тест показа меню с неверным выбором."""
        mock_console = Mock()
        menu = MainMenuScreen(mock_console)
        
        # Мокаем ввод пользователя
        monkeypatch.setattr("builtins.input", lambda x: "10")
        
        result = menu.show()
        
        assert result == 3  # Должен вернуть 3 (в пределах 1-5)
        mock_console.print_error.assert_called_once()