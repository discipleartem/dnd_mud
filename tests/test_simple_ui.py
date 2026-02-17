"""
Упрощенные безопасные тесты для UI компонентов.

Эти тесты проверяют функциональность без зависимостей от точных промптов.
"""

import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.renderer import Renderer
from src.infrastructure.ui.input_handler import InputHandler


class TestSimpleRenderer:
    """Упрощенные тесты рендерера."""

    def setup_method(self):
        """Настраивает тесты."""
        self.renderer = Renderer()

    @patch("sys.platform", "linux")
    @patch("builtins.print")
    def test_clear_screen_linux(self, mock_print):
        """Тестирует очистку экрана в Linux."""
        self.renderer.clear_screen()
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_show_title(self, mock_print):
        """Тестирует отображение заголовка."""
        self.renderer.show_title("Тестовый заголовок")
        assert mock_print.call_count >= 3  # border, title, border

    @patch("builtins.print")
    def test_show_error(self, mock_print):
        """Тестирует отображение ошибки."""
        self.renderer.show_error("Тестовая ошибка")
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_show_success(self, mock_print):
        """Тестирует отображение успеха."""
        self.renderer.show_success("Тестовый успех")
        mock_print.assert_called_once()

    @patch("builtins.print")
    def test_show_info(self, mock_print):
        """Тестирует отображение информации."""
        self.renderer.show_info("Тестовая информация")
        mock_print.assert_called_once()


class TestSimpleInputHandler:
    """Упрощенные тесты обработчика ввода."""

    def setup_method(self):
        """Настраивает тесты."""
        self.input_handler = InputHandler()

    @patch("builtins.input")
    def test_get_menu_choice_valid(self, mock_input):
        """Тестирует получение корректного выбора меню."""
        mock_input.return_value = "2"

        result = self.input_handler.get_menu_choice(5)

        assert result == 2
        assert mock_input.called

    @patch("builtins.input")
    def test_get_menu_choice_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в выборе меню."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_menu_choice(5)

        assert result == 5  # Возвращает последний пункт

    @patch("builtins.input")
    def test_get_text_input(self, mock_input):
        """Тестирует получение текстового ввода."""
        mock_input.return_value = "тестовый текст"

        result = self.input_handler.get_text_input("Введите текст: ")

        assert result == "тестовый текст"
        assert mock_input.called

    @patch("builtins.input")
    def test_get_string_basic(self, mock_input):
        """Тестирует базовое получение строки."""
        mock_input.return_value = "тестовая строка"

        result = self.input_handler.get_string("Введите строку: ")

        assert result == "тестовая строка"
        assert mock_input.called

    @patch("builtins.input")
    def test_get_string_with_default(self, mock_input):
        """Тестирует получение строки с значением по умолчанию."""
        mock_input.return_value = ""

        result = self.input_handler.get_string(
            "Введите строку: ", "значение по умолчанию"
        )

        assert result == "значение по умолчанию"
        assert mock_input.called

    @patch("builtins.input")
    def test_get_int_basic(self, mock_input):
        """Тестирует базовое получение целого числа."""
        mock_input.return_value = "42"

        result = self.input_handler.get_int("Введите число: ")

        assert result == 42
        assert mock_input.called

    @patch("builtins.input")
    def test_get_int_with_default(self, mock_input):
        """Тестирует получение числа со значением по умолчанию."""
        mock_input.return_value = ""

        result = self.input_handler.get_int("Введите число: ", default=10)

        assert result == 10
        assert mock_input.called

    @patch("builtins.input")
    def test_get_int_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в вводе числа."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_int("Введите число: ", default=10, min_value=1)

        assert result == 10  # Возвращает значение по умолчанию

    @patch("builtins.input")
    def test_wait_for_enter(self, mock_input):
        """Тестирует ожидание нажатия Enter."""
        self.input_handler.wait_for_enter("Нажмите Enter...")

        mock_input.assert_called_once()

    @patch("builtins.input")
    def test_wait_for_enter_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в ожидании Enter."""
        mock_input.side_effect = KeyboardInterrupt()

        # Не должно вызывать исключение
        self.input_handler.wait_for_enter()

        mock_input.assert_called_once()


class TestBasicFunctionality:
    """Тесты базовой функциональности."""

    def test_renderer_initialization(self):
        """Тестирует инициализацию рендерера."""
        renderer = Renderer()
        assert renderer is not None

    def test_input_handler_initialization(self):
        """Тестирует инициализацию обработчика ввода."""
        handler = InputHandler()
        assert handler is not None

    @patch("builtins.input")
    def test_simple_workflow(self, mock_input):
        """Тестирует простой рабочий процесс."""
        handler = InputHandler()
        _renderer = Renderer()  # Создается для полноты теста

        # Настройка моков
        mock_input.side_effect = ["Тестовый персонаж", "5", "2"]

        # Имитируем простой ввод
        name = handler.get_string("Введите имя: ")
        level = handler.get_int("Введите уровень: ", min_value=1, max_value=20)
        choice = handler.get_menu_choice(5)

        # Проверяем результаты
        assert name == "Тестовый персонаж"
        assert level == 5
        assert choice == 2
        assert mock_input.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
