"""Тесты для консольного интерфейса.

Следует принципам:
- KISS: Простые и понятные тесты
- YAGNI: Только необходимый функционал
"""

from unittest.mock import Mock, patch

from src.ui.console import Console


class TestConsole:
    """Тесты для консольного интерфейса."""

    def test_init_without_colorama(self) -> None:
        """Тест инициализации без colorama."""
        with patch('builtins.__import__', side_effect=ImportError):
            console = Console()
            assert console._has_colorama is False

    @patch('builtins.print')
    def test_clear(self, mock_print: Mock) -> None:
        """Тест очистки экрана."""
        console = Console()
        console.clear()

        mock_print.assert_called_once_with("\033[2J\033[H", end="")

    @patch('builtins.print')
    def test_print_info_no_color(self, mock_print: Mock) -> None:
        """Тест печати информационного сообщения без цвета."""
        console = Console()
        console._has_colorama = False

        console.print_info("Тестовое сообщение")

        mock_print.assert_called_once_with("Тестовое сообщение")

    @patch('builtins.print')
    def test_print_error_no_color(self, mock_print: Mock) -> None:
        """Тест печати ошибки без цвета."""
        console = Console()
        console._has_colorama = False

        console.print_error("Ошибка")

        mock_print.assert_called_once_with("Ошибка")

    @patch('builtins.print')
    def test_print_success_no_color(self, mock_print: Mock) -> None:
        """Тест печати успеха без цвета."""
        console = Console()
        console._has_colorama = False

        console.print_success("Успех")

        mock_print.assert_called_once_with("Успех")

    def test_get_input(self) -> None:
        """Тест получения ввода."""
        console = Console()

        with patch('builtins.input', return_value="test"):
            result = console.get_input("Введите: ")
            assert result == "test"

    def test_get_int_input_success(self) -> None:
        """Тест успешного получения числового ввода."""
        console = Console()

        with patch.object(console, "get_input", return_value="42"):
            result = console.get_int_input("Число: ")
            assert result == 42

    def test_get_int_input_validation(self) -> None:
        """Тест валидации числового ввода."""
        console = Console()

        with patch.object(console, "get_input", side_effect=["abc", "42"]):
            with patch.object(console, "print_error") as mock_error:
                result = console.get_int_input("Число: ")
                assert result == 42
                mock_error.assert_called_once_with("Пожалуйста, введите целое число.")

    @patch('builtins.print')
    def test_show_message_and_wait(self, mock_print: Mock) -> None:
        """Тест показа сообщения и ожидания ввода."""
        console = Console()

        with patch.object(console, "print_info") as mock_info:
            with patch.object(console, "get_input") as mock_input:
                console.show_message_and_wait("Тестовое сообщение")

                mock_info.assert_called_once_with("Тестовое сообщение")
                mock_input.assert_called_once_with("Нажмите Enter для продолжения...")
