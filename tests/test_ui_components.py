"""
Тесты для UI компонентов - Renderer и InputHandler.

Тестируем:
- Очистку экрана
- Отображение заголовков и меню
- Цветовые сообщения (ошибки, успех, информация)
- Обработку пользовательского ввода
- Валидацию ввода
- Обработку исключений
"""

import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.infrastructure.ui.renderer import Renderer, renderer
from src.infrastructure.ui.input_handler import InputHandler, input_handler

pytestmark = pytest.mark.unit


class TestRenderer:
    """Тесты рендерера."""

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

        # Проверяем вызовы print
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("=" * 70 in call for call in calls)
        assert any("Тестовый заголовок" in call for call in calls)

    @patch("builtins.print")
    def test_show_title_with_subtitle(self, mock_print):
        """Тестирует отображение заголовка с подзаголовком."""
        self.renderer.show_title("Тестовый заголовок", "Тестовый подзаголовок")

        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Тестовый заголовок" in call for call in calls)
        assert any("Тестовый подзаголовок" in call for call in calls)

    @patch("builtins.print")
    def test_render_title_alias(self, mock_print):
        """Тестирует псевдоним render_title."""
        with patch.object(self.renderer, "show_title") as mock_show_title:
            self.renderer.render_title("Тестовый заголовок")
            mock_show_title.assert_called_once_with("Тестовый заголовок")

    @patch("builtins.print")
    def test_show_menu(self, mock_print):
        """Тестирует отображение меню."""
        options = [{"text": "Опция 1"}, {"text": "Опция 2"}, {"text": "Опция 3"}]

        self.renderer.show_menu("Тестовое меню", options)

        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Тестовое меню" in call for call in calls)
        assert any("1. Опция 1" in call for call in calls)
        assert any("2. Опция 2" in call for call in calls)
        assert any("3. Опция 3" in call for call in calls)

    @patch("builtins.print")
    def test_show_error(self, mock_print):
        """Тестирует отображение ошибки."""
        self.renderer.show_error("Тестовая ошибка")

        mock_print.assert_called_once_with(
            "\033[1;31m❌ ОШИБКА: Тестовая ошибка\033[0m"
        )

    @patch("builtins.print")
    def test_render_error_alias(self, mock_print):
        """Тестирует псевдоним render_error."""
        with patch.object(self.renderer, "show_error") as mock_show_error:
            self.renderer.render_error("Тестовая ошибка")
            mock_show_error.assert_called_once_with("Тестовая ошибка")

    @patch("builtins.print")
    def test_show_success(self, mock_print):
        """Тестирует отображение успеха."""
        self.renderer.show_success("Тестовый успех")

        mock_print.assert_called_once_with("\033[1;32m✓ Тестовый успех\033[0m")

    @patch("builtins.print")
    def test_render_success_alias(self, mock_print):
        """Тестирует псевдоним render_success."""
        with patch.object(self.renderer, "show_success") as mock_show_success:
            self.renderer.render_success("Тестовый успех")
            mock_show_success.assert_called_once_with("Тестовый успех")

    @patch("builtins.print")
    def test_show_info(self, mock_print):
        """Тестирует отображение информации."""
        self.renderer.show_info("Тестовая информация")

        mock_print.assert_called_once_with("\033[1;34mℹ Тестовая информация\033[0m")

    @patch("builtins.print")
    def test_render_info_alias(self, mock_print):
        """Тестирует псевдоним render_info."""
        with patch.object(self.renderer, "show_info") as mock_show_info:
            self.renderer.render_info("Тестовая информация")
            mock_show_info.assert_called_once_with("Тестовая информация")

    @patch("builtins.input")
    def test_get_input(self, mock_input):
        """Тестирует получение ввода."""
        mock_input.return_value = "тестовый ввод"

        result = self.renderer.get_input("Промпт: ")

        assert result == "тестовый ввод"
        mock_input.assert_called_once_with("Промпт: ")


class TestInputHandler:
    """Тесты обработчика ввода."""

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
    @patch("builtins.print")
    def test_get_menu_choice_invalid_then_valid(self, mock_print, mock_input):
        """Тестирует некорректный ввод с последующим корректным."""
        # Ограничиваем количество вызовов чтобы избежать бесконечного цикла
        mock_input.side_effect = ["abc", "0", "6", "3"]

        result = self.input_handler.get_menu_choice(5)

        assert result == 3
        assert mock_input.call_count == 4
        # Проверяем сообщения об ошибках
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Пожалуйста, введите число" in call for call in calls)
        assert any("Пожалуйста, введите число от 1 до 5" in call for call in calls)

    @patch("builtins.input")
    def test_get_menu_choice_empty_input(self, mock_input):
        """Тестирует пустой ввод."""
        mock_input.side_effect = ["", "   ", "2"]

        result = self.input_handler.get_menu_choice(5)

        assert result == 2
        assert mock_input.call_count == 3

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
        mock_input.assert_called_once_with("Введите строку [значение по умолчанию]")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_string_empty_not_allowed(self, mock_print, mock_input):
        """Тестирует получение строки с запретом пустого ввода."""
        mock_input.side_effect = ["", "   ", "корректное значение"]

        result = self.input_handler.get_string("Введите строка", allow_empty=False)

        assert result == "корректное значение"
        assert mock_input.call_count == 3
        # Проверяем сообщения об ошибках
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Поле не может быть пустым" in call for call in calls)

    @patch("builtins.input")
    def test_get_string_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в вводе строки."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_string(
            "Введите строку: ", "значение по умолчанию"
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
    @patch("builtins.print")
    def test_get_int_validation_range(self, mock_print, mock_input):
        """Тестирует валидацию диапазона для целого числа."""
        mock_input.side_effect = [
            "5",
            "15",
            "12",
        ]  # 5 < min, 15 > max, 12 в диапазоне

        result = self.input_handler.get_int("Введите число", min_value=10, max_value=14)

        assert result == 12
        assert mock_input.call_count == 3
        # Проверяем сообщения об ошибках
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Значение должно быть не менее 10" in call for call in calls)
        assert any("Значение должно быть не более 14" in call for call in calls)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_get_int_invalid_format(self, mock_print, mock_input):
        """Тестирует некорректный формат числа."""
        mock_input.side_effect = [
            "abc",
            "12.5",
            "not a number",
            "15",
        ]

        result = self.input_handler.get_int("Введите число")

        assert result == 15
        assert mock_input.call_count == 4
        # Проверяем сообщения об ошибках
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Пожалуйста, введите корректное число" in call for call in calls)

    @patch("builtins.input")
    def test_get_int_keyboard_interrupt(self, mock_input):
        """Тестирует KeyboardInterrupt в вводе числа."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_int("Введите число: ", default=10, min_value=1)

        assert result == 10  # Возвращает значение по умолчанию

    @patch("builtins.input")
    def test_get_int_keyboard_interrupt_no_default(self, mock_input):
        """Тестирует KeyboardInterrupt без значения по умолчанию."""
        mock_input.side_effect = KeyboardInterrupt()

        result = self.input_handler.get_int("Введите число: ", min_value=5)

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

    @patch("builtins.input")
    def test_wait_for_enter_eof_error(self, mock_input):
        """Тестирует EOFError в ожидании Enter."""
        mock_input.side_effect = EOFError()

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


class TestUIIntegration:
    """Интеграционные тесты UI компонентов."""

    @pytest.mark.integration
    @patch("builtins.input")
    @patch("builtins.print")
    def test_complete_menu_interaction(self, mock_print, mock_input):
        """Тестирует полное взаимодействие с меню."""
        # Настройка UI компонентов
        test_renderer = Renderer()
        test_input_handler = InputHandler()

        # Имитируем выбор меню
        mock_input.side_effect = ["2"]  # Выбор второго пункта

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

    @patch("builtins.input")
    @patch("builtins.print")
    def test_character_creation_flow(self, mock_print, mock_input):
        """Тестируем поток создания персонажа."""
        test_renderer = Renderer()
        test_input_handler = InputHandler()

        # Имитируем ввод данных персонажа
        mock_input.side_effect = [
            "Тестовый персонаж",  # Имя
            "5",  # Уровень
            "1",  # Выбор метода генерации
            "1",  # Выбор расы
            "2",  # Выбор класса
            "1",  # Подтверждение
        ]

        # Шаг 1: Базовая информация
        test_renderer.show_title("Создание персонажа", "Шаг 1: Базовая информация")
        name = test_input_handler.get_string(
            "Введите имя персонажа", allow_empty=False
        )
        level = test_input_handler.get_int(
            "Введите уровень", min_value=1, max_value=20
        )

        # Шаг 2: Выбор расы и класса
        test_renderer.show_title("Создание персонажа", "Шаг 2: Раса и класс")
        race_choice = test_input_handler.get_int("Выберите расу", max_value=3)
        class_choice = test_input_handler.get_int("Выберите класс", max_value=5)

        # Показываем результат
        test_renderer.show_success(f"Создан персонаж: {name}, уровень {level}")
        test_renderer.show_info(f"Раса: {race_choice}, Класс: {class_choice}")

        assert name == "Тестовый персонаж"
        assert level == 5
        assert race_choice == 1
        assert class_choice == 1

        # Проверяем вызовы рендерера
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Создание персонажа" in call for call in calls)
        assert any(
            "✓ Создан персонаж: Тестовый персонаж, уровень 5" in call for call in calls
        )
        assert any("ℹ Раса: 1, Класс: 1" in call for call in calls)


class TestErrorHandling:
    """Тесты обработки ошибок в UI компонентах."""

    @pytest.mark.integration
    @patch("builtins.input")
    @patch("builtins.print")
    def test_multiple_error_recovery(self, mock_print, mock_input):
        """Тестирует восстановление после множественных ошибок."""
        test_input_handler = InputHandler()

        # Имитируем последовательность ошибок и успешный ввод
        mock_input.side_effect = [
            "abc",  # Не число
            "",  # Пусто
            "0",  # Меньше минимума
            "11",  # Больше максимума
            "5",  # Корректное значение
        ]

        result = test_input_handler.get_int(
            "Введите число (1-10): ", min_value=1, max_value=10
        )

        assert result == 5
        assert mock_input.call_count == 5

        # Проверяем сообщения об ошибках
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Пожалуйста, введите корректное число" in call for call in calls)
        assert any("Введите число" in call for call in calls)
        assert any("Значение должно быть не менее 1" in call for call in calls)
        assert any("Значение должно быть не более 10" in call for call in calls)

    @patch("builtins.input")
    def test_exception_propagation(self, mock_input):
        """Тестирует распространение исключений."""
        test_input_handler = InputHandler()

        # Вызываем неожиданное исключение
        mock_input.side_effect = RuntimeError("Неожиданная ошибка")

        # Должно вернуть значение по умолчанию или минимальное значение
        result = test_input_handler.get_int("Введите число", default=10)

        # В текущей реализации исключение будет перехвачено и возвращено значение по умолчанию
        assert result == 10


if __name__ == "__main__":
    pytest.main([__file__])
