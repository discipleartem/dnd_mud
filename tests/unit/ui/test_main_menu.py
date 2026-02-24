#!/usr/bin/env python3
"""Тесты для модулей главного меню."""

from unittest.mock import patch

from src.ui.main_menu.main import (
    CHARACTER_HANDLERS,
    MENU_HANDLERS,
    _is_valid_choice,
    _show_menu_header,
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
        # Ищем строку с заголовком (не "=" и не пустую)
        title_line = None
        for call in print_calls:
            if "Коротко" in call and "=" not in call:
                title_line = call
                break

        assert title_line is not None
        # Извлекаем саму строку из call объекта
        title_str = title_line.split("'")[1] if "'" in title_line else title_line
        assert len(title_str) == 40
        assert "Коротко" in title_str
        assert title_str.strip() == "Коротко"

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
            with patch('builtins.print'):
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
        mock_t.return_value = "Ошибка: введите число"

        result = _is_valid_choice("-1", 5)

        assert result is False
        mock_print.assert_called_once_with("Ошибка: введите число")
        mock_t.assert_called_once_with("menu.errors.invalid_number")

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
            with (
                patch('src.ui.main_menu.main.t') as mock_t,
                patch('builtins.print')
            ):
                mock_t.return_value = "Error"
                result = _is_valid_choice(choice, max_choice)
                assert result == expected


class TestMainMenu:
    """Тесты для функции main_menu."""

    def test_main_menu_character_creation_simple(self) -> None:
        """Простой тест создания персонажа через главное меню."""
        # Тестируем только структуру обработчиков
        assert 1 in CHARACTER_HANDLERS
        assert callable(CHARACTER_HANDLERS[1])

        # Проверяем, что обработчик возвращает Character
        from src.ui.adapters.character_adapter import Character
        # Проверяем тип возвращаемого значения через аннотацию
        handler = CHARACTER_HANDLERS[1]
        annotations = getattr(handler, '__annotations__', {})
        assert 'return' in annotations
        assert annotations['return'] == Character

    def test_main_menu_load_game_simple(self) -> None:
        """Простой тест загрузки игры через главное меню."""
        # Тестируем только структуру обработчиков
        assert 2 in MENU_HANDLERS
        assert callable(MENU_HANDLERS[2])

    def test_main_menu_settings_simple(self) -> None:
        """Простой тест настроек через главное меню."""
        # Тестируем только структуру обработчиков
        assert 3 in MENU_HANDLERS
        assert callable(MENU_HANDLERS[3])

    def test_main_menu_exit_simple(self) -> None:
        """Простой тест выхода из меню."""
        # Проверяем, что выход обрабатывается правильно
        # (выход - это пункт 4, который не в обработчиках)
        assert 4 not in CHARACTER_HANDLERS
        assert 4 not in MENU_HANDLERS
