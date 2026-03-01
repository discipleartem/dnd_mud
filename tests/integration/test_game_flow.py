"""Integration тесты полного игрового цикла."""

import pytest
from unittest.mock import Mock, patch

from src.core.game import Game
from src.ui.console import Console


class TestGameFlow:
    """Тесты полного цикла игры."""
    
    @pytest.fixture
    def mock_console(self):
        """Фикстура с мок консоли."""
        return Mock(spec=Console)
    
    @patch("ui.screen_factory.MainMenuScreen")
    def test_complete_game_flow(self, mock_main_menu, mock_console):
        """Тест полного цикла: меню → выход."""
        game = Game(mock_console)
        
        # Мокируем начальный ввод (нажатие Enter)
        mock_console.get_input.return_value = "1"
        
        # Мокируем show чтобы вернуть EXIT (5) и завершить цикл
        mock_main_menu.return_value.show.return_value = 5  # EXIT
        
        # Запускаем игру - она должна завершиться после одного цикла
        game.run()
        
        # Проверяем, что меню было показано
        mock_main_menu.assert_called_once()
        mock_main_menu.return_value.show.assert_called_once()
        
        # Проверяем, что игра завершилась
        assert game.running is False
    
    @patch("ui.screen_factory.MainMenuScreen")
    def test_game_keyboard_interrupt(self, mock_main_menu, mock_console):
        """Тест обработки KeyboardInterrupt."""
        game = Game(mock_console)
        
        # Мокируем KeyboardInterrupt на первом же вводе
        mock_console.get_input.side_effect = [KeyboardInterrupt()]
        
        with pytest.raises(KeyboardInterrupt):
            game.run()
        
        # Проверяем, что игра завершилась
        assert game.running is False
    
    @patch("ui.screen_factory.MainMenuScreen")
    def test_game_exception_handling(self, mock_main_menu, mock_console):
        """Тест обработки исключений."""
        game = Game(mock_console)
        
        # Мокируем начальный ввод (нажатие Enter)
        mock_console.get_input.return_value = "1"
        
        # Мокируем исключение в главном меню (один раз), затем EXIT,
        # чтобы игровой цикл завершился детерминированно.
        mock_main_menu.return_value.show.side_effect = [
            Exception("Тестовая ошибка"),
            5,  # EXIT
        ]
        
        # Запускаем игру - она должна обработать исключение и продолжить
        game.run()
        
        # Проверяем, что ошибка была обработана
        mock_console.print_error.assert_called_with("Ошибка: Тестовая ошибка")