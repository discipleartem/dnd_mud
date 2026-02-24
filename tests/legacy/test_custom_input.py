#!/usr/bin/env python3
"""Тестирование улучшенной функции get_user_choice."""


from src.ui.user_choice import get_user_choice


def test_custom_input() -> None:
    """Тест произвольного ввода."""
    from unittest.mock import patch

    # Простой тест без циклов - только custom_only
    with patch('builtins.input', return_value='тестовый текст'):
        result = get_user_choice(
            ["Пример 1", "Пример 2"],
            "Введите текст:",
            allow_cancel=False,
            custom_only=True,
        )
        assert result == "тестовый текст"

    # Тест отмены
    with patch('builtins.input', return_value='отмена'):
        result = get_user_choice(
            ["Вариант 1", "Вариант 2"],
            "Выберите вариант:",
            allow_cancel=True,
            cancel_text="отмена",
        )
        assert result is None

    # Тест выбора из списка
    with patch('builtins.input', return_value='2'):
        result = get_user_choice(
            ["Вариант 1", "Вариант 2", "Вариант 3"],
            "Выберите вариант:",
            allow_cancel=False,
        )
        assert result == "Вариант 2"


if __name__ == "__main__":
    test_custom_input()
