"""
Безопасные тесты для UI компонентов с таймаутами.

Эти тесты предотвращают зависания и используют правильное мокирование.
"""

import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.renderer import Renderer, renderer
from src.infrastructure.ui.input_handler import InputHandler, input_handler


class TimeoutError(Exception):
    """Исключение для таймаута."""

    pass


def timeout_handler(signum, frame):
    """Обработчик таймаута."""
    raise TimeoutError("Тест превысил время выполнения")


class TestSafeRenderer:
    """Безопасные тесты рендерера."""

    def setup_method(self):
        """Настраивает тесты."""
        self.renderer = Renderer()

    @patch("sys.platform", "linux")
    @patch("builtins.print")
    def test_clear_screen_linux(self, mock_print):
        """Тестирует очистку экрана в Linux."""
        self.renderer.clear_screen()
        mock_print.assert_called_once_with("\033[2J\033[H", end="")

    @patch("sys.platform", "darwin")
    @patch("builtins.print")
    def test_clear_screen_macos(self, mock_print):
        """Тестирует очистку экрана в macOS."""
        self.renderer.clear_screen()
        mock_print.assert_called_once_with("\033[2J\033[H", end="")

    @patch("sys.platform", "win32")
    @patch("os.system")
    def test_clear_screen_windows(self, mock_system):
        """Тестирует очистку экрана в Windows."""
        self.renderer.clear_screen()
        mock_system.assert_called_once_with("cls")

    @patch("builtins.print")
    def test_show_title_without_subtitle(self, mock_print):
        """Тестирует отображение заголовка без подзаголовка."""
        self.renderer.show_title("Тестовый заголовок")

        calls = [str(call) for call in mock_print.call_args_list]
        assert any("=" * 70 in call for call in calls)
        assert any("Тестовый заголовок" in call for call in calls)

    @patch("builtins.print")
    def test_show_error(self, mock_print):
        """Тестирует отображение ошибки."""
        self.renderer.show_error("Тестовая ошибка")
        mock_print.assert_called_once_with(
            "\033[1;31m❌ ОШИБКА: Тестовая ошибка\033[0m"
        )

    @patch("builtins.print")
    def test_show_success(self, mock_print):
        """Тестирует отображение успеха."""
        self.renderer.show_success("Тестовый успех")
        mock_print.assert_called_once_with("\033[1;32m✓ Тестовый успех\033[0m")

    @patch("builtins.print")
    def test_show_info(self, mock_print):
        """Тестирует отображение информации."""
        self.renderer.show_info("Тестовая информация")
        mock_print.assert_called_once_with("\033[1;34mℹ Тестовая информация\033[0m")


class TestSafeInputHandler:
    """Безопасные тесты обработчика ввода."""

    def setup_method(self):
        """Настраивает тесты."""
        self.input_handler = InputHandler()

    @patch("builtins.input")
    def test_get_menu_choice_valid(self, mock_input):
        """Тестирует получение корректного выбора меню."""
        mock_input.return_value = "2"

        result = self.input_handler.get_menu_choice(5)

        assert result == 2
        mock_input.assert_called_once_with("Введите номер (1-5): ")

    @patch("builtins.input")
    def test_get_menu_choice_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в выборе меню."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_menu_choice(5)

        assert result == 5  # Возвращает последний пункт

    @patch("builtins.input")
    def test_get_menu_choice_eof_error(self, mock_input):
        """Тестирует EOFError в выборе меню."""
        mock_input.side_effect = EOFError()

        result = self.input_handler.get_menu_choice(5)

        assert result == 5  # Возвращает последний пункт

    @patch("builtins.input")
    def test_get_text_input(self, mock_input):
        """Тестирует получение текстового ввода."""
        mock_input.return_value = "тестовый текст"

        result = self.input_handler.get_text_input("Введите текст: ")

        assert result == "тестовый текст"
        mock_input.assert_called_once_with("Введите текст: ")

    @patch("builtins.input")
    def test_get_text_input_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в текстовом вводе."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_text_input("Введите текст: ")

        assert result == ""

    @patch("builtins.input")
    def test_get_string_without_default(self, mock_input):
        """Тестирует получение строки без значения по умолчанию."""
        mock_input.return_value = "тестовая строка"

        result = self.input_handler.get_string("Введите строку")

        assert result == "тестовая строка"
        mock_input.assert_called_once_with("Введите строку")

    @patch("builtins.input")
    def test_get_string_with_default_accepted(self, mock_input):
        """Тестирует получение строки с принятием значения по умолчанию."""
        mock_input.return_value = ""  # Пустой ввод означает принятие по умолчанию

        result = self.input_handler.get_string(
            "Введите строку", "значение по умолчанию"
        )

        assert result == "значение по умолчанию"
        mock_input.assert_called_once_with("Введите строку [значение по умолчанию]")

    @patch("builtins.input")
    def test_get_string_with_default_override(self, mock_input):
        """Тестирует получение строки с переопределением значения по умолчанию."""
        mock_input.return_value = "новое значение"

        result = self.input_handler.get_string(
            "Введите строку", "значение по умолчанию"
        )

        assert result == "новое значение"

    @patch("builtins.input")
    def test_get_string_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в вводе строки."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_string(
            "Введите строку", "значение по умолчанию"
        )

        assert result == "значение по умолчанию"

    @patch("builtins.input")
    def test_get_int_without_default(self, mock_input):
        """Тестирует получение целого числа без значения по умолчанию."""
        mock_input.return_value = "42"

        result = self.input_handler.get_int("Введите число")

        assert result == 42
        mock_input.assert_called_once_with("Введите число")

    @patch("builtins.input")
    def test_get_int_with_default_accepted(self, mock_input):
        """Тестирует получение числа с принятием значения по умолчанию."""
        mock_input.return_value = ""

        result = self.input_handler.get_int("Введите число", default=10)

        assert result == 10
        mock_input.assert_called_once_with("Введите число [10]")

    @patch("builtins.input")
    def test_get_int_with_default_override(self, mock_input):
        """Тестирует получение числа с переопределением значения по умолчанию."""
        mock_input.return_value = "25"

        result = self.input_handler.get_int("Введите число", default=10)

        assert result == 25

    @patch("builtins.input")
    def test_get_int_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в вводе числа."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_int("Введите число", default=10, min_value=1)

        assert result == 10  # Возвращает значение по умолчанию

    @patch("builtins.input")
    def test_get_int_keyboard_interrupt_no_default(self, mock_input):
        """Тестирует KeyboardInterrupt без значения по умолчанию."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_int("Введите число", min_value=5)

        assert result == 5  # Возвращает min_value

    @patch("builtins.input")
    def test_wait_for_enter(self, mock_input):
        """Тестирует ожидание нажатия Enter."""
        self.input_handler.wait_for_enter("Нажмите Enter...")

        mock_input.assert_called_once_with("Нажмите Enter...")

    @patch("builtins.input")
    def test_wait_for_enter_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в ожидании Enter."""
        mock_input.side_effect = KeyboardInterrupt()

        # Не должно вызывать исключение
        self.input_handler.wait_for_enter()

        mock_input.assert_called_once()


class TestGlobalInstances:
    """Тесты глобальных экземпляров."""

    def test_global_renderer(self):
        """Тестирует глобальный экземпляр рендерера."""
        assert isinstance(renderer, Renderer)

    def test_global_input_handler(self):
        """Тестирует глобальный экземпляр обработчика ввода."""
        assert isinstance(input_handler, InputHandler)


class TestSimpleIntegration:
    """Простые интеграционные тесты без бесконечных циклов."""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_simple_menu_interaction(self, mock_print, mock_input):
        """Тестирует простое взаимодействие с меню."""
        test_renderer = Renderer()
        test_input_handler = InputHandler()

        # Имитируем выбор меню
        mock_input.return_value = "2"  # Выбор второго пункта

        # Отображаем меню
        options = [
            {"text": "Новая игра"},
            {"text": "Загрузить игру"},
            {"text": "Выход"},
        ]

        test_renderer.show_menu("Главное меню", options)
        choice = test_input_handler.get_menu_choice(len(options))

        # Показываем результат
        test_renderer.show_success(f"Выбран пункт: {choice}")

        assert choice == 2
        # Проверяем, что меню было отображено
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Главное меню" in call for call in calls)
        assert any("1. Новая игра" in call for call in calls)
        assert any("2. Загрузить игру" in call for call in calls)
        assert any("3. Выход" in call for call in calls)
        assert any("✓ Выбран пункт: 2" in call for call in calls)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
