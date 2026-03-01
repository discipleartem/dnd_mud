"""Тесты консоли."""

import sys
from io import StringIO
from unittest.mock import patch

# Добавляем src в Python path для тестов
sys.path.insert(0, 'src')


def test_console_basic_no_colorama():
    """Тест базовой функциональности консоли без colorama."""
    if 'colorama' in sys.modules:
        del sys.modules['colorama']

    with patch('ui.console.Console._init_colorama', return_value=None):
        from ui.console import Console

        captured_output = StringIO()
        console = Console()

        with patch('sys.stdout', captured_output):
            console.clear()
            console.print_info("Тестовое сообщение")
            console.print_success("Успех")
            console.print_error("Ошибка")
            console.print_menu_item(1, "Пункт меню")
            console.print_separator()

            output = captured_output.getvalue()

            assert "Тестовое сообщение" in output
            assert "Успех" in output
            assert "Ошибка" in output
            assert "1. Пункт меню" in output

            assert "\x1b[" in output  # ANSI escape последовательности для clear


def test_console_with_colorama():
    """Тест консоли с доступным colorama."""
    mock_colorama = patch('ui.console.Console._init_colorama')
    mock_colorama.return_value = True

    with mock_colorama:
        from ui.console import Console

        captured_output = StringIO()
        console = Console()

        with patch('sys.stdout', captured_output):
            console.print_info("Тест с цветом")
            console.print_success("Зеленый текст")
            console.print_error("Красный текст")

            output = captured_output.getvalue()

            assert "Тест с цветом" in output
            assert "Зеленый текст" in output
            assert "Красный текст" in output


def test_get_int_input():
    """Тест получения числового ввода."""
    with patch('ui.console.Console._init_colorama', return_value=None):
        from ui.console import Console

        console = Console()

        with patch.object(console, 'get_input', return_value='42'):
            result = console.get_int_input("Введите число: ")
            assert result == 42

        with patch.object(console, 'get_input', side_effect=['abc', '42']):
            with patch.object(console, 'print_error') as mock_error:
                result = console.get_int_input("Введите число: ")
                assert result == 42
                assert mock_error.call_count == 1
                mock_error.assert_called_with(
                    "Пожалуйста, введите целое число."
                )


def test_is_valid_range():
    """Тест валидации диапазона."""
    with patch('ui.console.Console._init_colorama', return_value=None):
        from ui.console import Console

        console = Console()

        assert console._is_valid_range(5, 1, 10) is True

        with patch.object(console, 'print_error') as mock_error:
            assert console._is_valid_range(0, 1, 10) is False
            mock_error.assert_called_with("Значение должно быть не менее 1")

        with patch.object(console, 'print_error') as mock_error:
            assert console._is_valid_range(15, 1, 10) is False
            mock_error.assert_called_with("Значение должно быть не более 10")
