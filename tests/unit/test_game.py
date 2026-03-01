"""Тесты для основной игры."""

from unittest.mock import Mock, patch

from core.constants import GOODBYE_MESSAGE, PRESS_ENTER, WELCOME_MESSAGE
from src.core.game import Game


class TestGame:
    """Тесты для основной игры."""

    def test_init(self) -> None:
        """Тест инициализации игры."""
        ui = Mock()
        game = Game(ui)

        assert game.ui == ui
        assert game.running is False
        assert game.game_use_case is not None

    def test_run_keyboard_interrupt(self) -> None:
        """Тест прерывания по Ctrl+C."""
        ui = Mock()
        game = Game(ui)

        with patch.object(game.game_use_case, 'show_and_handle_menu', side_effect=KeyboardInterrupt()):
            game.run()

        assert game.running is True  # Устанавливается в начале run()
        ui.print_success.assert_called_with(f"\n{GOODBYE_MESSAGE}")

    @patch('builtins.print')
    def test_run_exception(self, mock_print: Mock) -> None:
        """Тест обработки исключений."""
        ui = Mock()
        game = Game(ui)

        # Создаем счетчик для первого вызова - исключение, второго - False для выхода
        call_count = 0

        def side_effect_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Тестовая ошибка")
            return False  # Выход из цикла на втором вызове

        with patch.object(game.game_use_case, 'show_and_handle_menu', side_effect=side_effect_func):
            game.run()

        ui.print_error.assert_called_with("Ошибка: Тестовая ошибка")
        ui.get_input.assert_called_with(PRESS_ENTER)

    def test_run_normal_flow(self) -> None:
        """Тест нормального потока выполнения."""
        ui = Mock()
        ui.get_input.return_value = ""

        # Use case возвращает False для завершения цикла
        game_use_case = Mock()
        game_use_case.show_and_handle_menu.return_value = False

        game = Game(ui)
        game.game_use_case = game_use_case

        game.run()

        # Проверяем последовательность вызовов
        ui.clear.assert_called_once()
        ui.print_info.assert_called_once_with(WELCOME_MESSAGE)
        ui.get_input.assert_called_with(PRESS_ENTER)
        game_use_case.show_and_handle_menu.assert_called_once()
