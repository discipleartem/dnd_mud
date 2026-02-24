#!/usr/bin/env python3
"""Тесты для модулей главного меню."""

from unittest.mock import Mock, patch

import pytest

from src.ui.entities.character import Character
from src.ui.main_menu.main import (
    CHARACTER_HANDLERS,
    MENU_HANDLERS,
    _is_valid_choice,
    _show_menu_header,
    main_menu,
)


class TestMainMenuConstants:
    """Тесты констант главного меню."""

    def test_menu_handlers_structure(self) -> None:
        """Тест структуры обработчиков меню."""
        assert isinstance(MENU_HANDLERS, dict)
        assert 2 in MENU_HANDLERS
        assert 3 in MENU_HANDLERS
        assert callable(MENU_HANDLERS[2])
        assert callable(MENU_HANDLERS[3])

    def test_character_handlers_structure(self) -> None:
        """Тест структуры обработчиков персонажей."""
        assert isinstance(CHARACTER_HANDLERS, dict)
        assert 1 in CHARACTER_HANDLERS
        assert callable(CHARACTER_HANDLERS[1])

    def test_handlers_imports(self) -> None:
        """Тест импортов обработчиков."""
        # Проверяем, что обработчики импортированы правильно
        from src.ui.main_menu.load_game import load_game
        from src.ui.main_menu.new_game import new_game
        from src.ui.main_menu.settings import settings
        
        assert MENU_HANDLERS[2] is load_game
        assert MENU_HANDLERS[3] is settings
        assert CHARACTER_HANDLERS[1] is new_game


class TestShowMenuHeader:
    """Тесты для функции _show_menu_header."""

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_show_menu_header_with_string_title(self, mock_print, mock_t) -> None:
        """Тест отображения заголовка со строковым названием."""
        mock_t.return_value = "D&D MUD"
        
        _show_menu_header()
        
        # Проверяем вызовы print
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Должно быть 3 вызова: рамка, заголовок, рамка
        assert len(print_calls) == 3
        assert "========================================" in print_calls[0]
        assert "D&D MUD" in print_calls[1]
        assert "========================================" in print_calls[2]

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_show_menu_header_with_non_string_title(self, mock_print, mock_t) -> None:
        """Тест отображения заголовка с не-строковым названием."""
        mock_t.return_value = {"title": "D&D MUD"}  # Не-строковый результат
        
        _show_menu_header()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Название должно быть преобразовано в строку
        assert "{'title': 'D&D MUD'}" in print_calls[1]

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_show_menu_header_centering(self, mock_print, mock_t) -> None:
        """Тест центрирования заголовка."""
        mock_t.return_value = "Коротко"
        
        _show_menu_header()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Заголовок должен быть отцентрирован в 40 символов
        title_line = print_calls[1]
        assert len(title_line) == 40
        assert "Коротко" in title_line
        assert title_line.strip() == "Коротко"

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_show_menu_header_long_title(self, mock_print, mock_t) -> None:
        """Тест отображения длинного заголовка."""
        mock_t.return_value = "Очень длинное название меню которое может не поместиться"
        
        _show_menu_header()
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Даже длинное название должно быть выведено
        title_line = print_calls[1]
        assert "Очень длинное название меню которое может не поместиться" in title_line


class TestIsValidChoice:
    """Тесты для функции _is_valid_choice."""

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_valid_number(self, mock_print, mock_t) -> None:
        """Тест валидного числового выбора."""
        result = _is_valid_choice("2", 5)
        
        assert result is True
        mock_print.assert_not_called()
        mock_t.assert_not_called()

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_boundary_values(self, mock_print, mock_t) -> None:
        """Тест граничных значений."""
        # Минимальное значение
        result = _is_valid_choice("1", 5)
        assert result is True
        
        # Максимальное значение
        result = _is_valid_choice("5", 5)
        assert result is True
        
        # Ниже минимума
        result = _is_valid_choice("0", 5)
        assert result is False
        
        # Выше максимума
        result = _is_valid_choice("6", 5)
        assert result is False

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_non_digit(self, mock_print, mock_t) -> None:
        """Тест не-цифрового выбора."""
        mock_t.return_value = "Ошибка: введите число"
        
        result = _is_valid_choice("abc", 5)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: введите число")
        mock_t.assert_called_once_with("menu.errors.invalid_number")

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_empty_string(self, mock_print, mock_t) -> None:
        """Тест пустой строки."""
        mock_t.return_value = "Ошибка: введите число"
        
        result = _is_valid_choice("", 5)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: введите число")
        mock_t.assert_called_once_with("menu.errors.invalid_number")

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_special_characters(self, mock_print, mock_t) -> None:
        """Тест специальных символов."""
        mock_t.return_value = "Ошибка: введите число"
        
        invalid_inputs = ["12.5", "-1", "1a", "a1", "!", "@", "#", " "]
        
        for invalid_input in invalid_inputs:
            with patch('builtins.print') as mock_print_inner:
                result = _is_valid_choice(invalid_input, 5)
                assert result is False

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_whitespace(self, mock_print, mock_t) -> None:
        """Тест пробельных символов."""
        mock_t.return_value = "Ошибка: введите число"
        
        result = _is_valid_choice("   ", 5)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: введите число")
        mock_t.assert_called_once_with("menu.errors.invalid_number")

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_negative_number(self, mock_print, mock_t) -> None:
        """Тест отрицательного числа."""
        mock_t.return_value = "Ошибка: число должно быть от 1 до 5"
        
        result = _is_valid_choice("-1", 5)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: число должно быть от 1 до 5")
        mock_t.assert_called_once_with("menu.errors.invalid_range")

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_zero(self, mock_print, mock_t) -> None:
        """Тест нуля."""
        mock_t.return_value = "Ошибка: число должно быть от 1 до 5"
        
        result = _is_valid_choice("0", 5)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: число должно быть от 1 до 5")
        mock_t.assert_called_once_with("menu.errors.invalid_range")

    @patch('src.ui.main_menu.main.t')
    @patch('builtins.print')
    def test_is_valid_choice_too_large(self, mock_print, mock_t) -> None:
        """Тест слишком большого числа."""
        mock_t.return_value = "Ошибка: число должно быть от 1 до 3"
        
        result = _is_valid_choice("10", 3)
        
        assert result is False
        mock_print.assert_called_once_with("Ошибка: число должно быть от 1 до 3")
        mock_t.assert_called_once_with("menu.errors.invalid_range")

    def test_is_valid_choice_different_max_values(self) -> None:
        """Тест разных максимальных значений."""
        # Тестируем с разными максимальными значениями
        test_cases = [
            ("1", 1, True),
            ("2", 1, False),
            ("3", 10, True),
            ("11", 10, False),
        ]
        
        for choice, max_choice, expected in test_cases:
            with patch('src.ui.main_menu.main.t') as mock_t, \
                 patch('builtins.print') as mock_print:
                mock_t.return_value = "Error"
                result = _is_valid_choice(choice, max_choice)
                assert result == expected


class TestMainMenu:
    """Тесты для функции main_menu."""

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_character_creation(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест создания персонажа через главное меню."""
        # Настройка моков
        mock_input.side_effect = ["1", "exit"]  # Сначала выбираем 1, потом выходим
        mock_is_valid.side_effect = [True, False]  # Первый выбор валиден, второй нет
        
        with patch('src.ui.main_menu.main.new_game') as mock_new_game:
            mock_character = Character(name="Тестовый персонаж")
            mock_new_game.return_value = mock_character
            
            with patch('sys.exit') as mock_exit:
                main_menu()
                
                # Проверяем, что new_game был вызван
                mock_new_game.assert_called_once()
                
                # Проверяем, что программа вышла
                mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_load_game(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест загрузки игры через главное меню."""
        mock_input.side_effect = ["2", "exit"]
        mock_is_valid.side_effect = [True, False]
        
        with patch('src.ui.main_menu.main.load_game') as mock_load_game:
            with patch('sys.exit') as mock_exit:
                main_menu()
                
                mock_load_game.assert_called_once()
                mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_settings(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест настроек через главное меню."""
        mock_input.side_effect = ["3", "exit"]
        mock_is_valid.side_effect = [True, False]
        
        with patch('src.ui.main_menu.main.settings') as mock_settings:
            with patch('sys.exit') as mock_exit:
                main_menu()
                
                mock_settings.assert_called_once()
                mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_invalid_choice_then_retry(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест неверного выбора с повторной попыткой."""
        mock_input.side_effect = ["invalid", "1", "exit"]
        mock_is_valid.side_effect = [False, True, False]
        
        with patch('src.ui.main_menu.main.new_game') as mock_new_game:
            mock_character = Character(name="Тестовый персонаж")
            mock_new_game.return_value = mock_character
            
            with patch('sys.exit') as mock_exit:
                main_menu()
                
                # Проверяем, что была попытка повторного ввода
                assert mock_input.call_count == 3
                assert mock_is_valid.call_count == 3
                mock_new_game.assert_called_once()
                mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_exit_directly(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест прямого выхода из меню."""
        mock_input.side_effect = ["exit"]
        mock_is_valid.return_value = False
        
        with patch('sys.exit') as mock_exit:
            main_menu()
            
            mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_multiple_invalid_choices(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест множественных неверных выборов."""
        mock_input.side_effect = ["abc", "123", "0", "10", "1", "exit"]
        mock_is_valid.side_effect = [False, False, False, False, True, False]
        
        with patch('src.ui.main_menu.main.new_game') as mock_new_game:
            mock_character = Character(name="Тестовый персонаж")
            mock_new_game.return_value = mock_character
            
            with patch('sys.exit') as mock_exit:
                main_menu()
                
                # Проверяем, что было несколько попыток ввода
                assert mock_input.call_count == 6
                assert mock_is_valid.call_count == 6
                mock_new_game.assert_called_once()
                mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_character_handler_exception(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест обработки исключения в обработчике персонажа."""
        mock_input.side_effect = ["1", "exit"]
        mock_is_valid.side_effect = [True, False]
        
        with patch('src.ui.main_menu.main.new_game') as mock_new_game:
            mock_new_game.side_effect = Exception("Test exception")
            
            with patch('sys.exit') as mock_exit:
                with pytest.raises(Exception, match="Test exception"):
                    main_menu()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_menu_handler_exception(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест обработки исключения в обработчике меню."""
        mock_input.side_effect = ["2", "exit"]
        mock_is_valid.side_effect = [True, False]
        
        with patch('src.ui.main_menu.main.load_game') as mock_load_game:
            mock_load_game.side_effect = Exception("Load game error")
            
            with patch('sys.exit') as mock_exit:
                with pytest.raises(Exception, match="Load game error"):
                    main_menu()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_unexpected_choice(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест неожиданного выбора (не в обработчиках)."""
        mock_input.side_effect = ["99", "exit"]
        mock_is_valid.side_effect = [True, False]
        
        with patch('sys.exit') as mock_exit:
            main_menu()
            
            # Программа должна просто продолжить работу и выйти
            mock_exit.assert_called_once()

    @patch('src.ui.main_menu.main._show_menu_header')
    @patch('src.ui.main_menu.main._is_valid_choice')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_menu_keyboard_interrupt(self, mock_print, mock_input, mock_is_valid, mock_show_header) -> None:
        """Тест прерывания с клавиатуры."""
        mock_input.side_effect = KeyboardInterrupt()
        
        with patch('sys.exit') as mock_exit:
            with pytest.raises(KeyboardInterrupt):
                main_menu()