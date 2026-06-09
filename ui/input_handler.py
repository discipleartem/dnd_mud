"""Валидация пользовательского ввода с повторным запросом."""

from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from ui.window_manager import print_wrapped


def get_int_input(
    prompt: str,
    min_val: int,
    max_val: int,
    loc: Any | None = None,
) -> int:
    """Запросить у пользователя целое число в диапазоне [min_val, max_val].

    Args:
        prompt: Приглашение для ввода
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение
        loc: Объект локализации (для сообщений об ошибках)

    Returns:
        Корректно введённое число
    """
    while True:
        try:
            raw = input(f'{Fore.CYAN}{prompt}{Style.RESET_ALL}')
            value = int(raw.strip())
            if min_val <= value <= max_val:
                return value

            error_msg = (
                loc('errors.invalid_input', min=min_val, max=max_val)
                if loc
                else f'Ошибка: введите число от {min_val} до {max_val}'
            )
            print_wrapped(error_msg, color=Fore.RED)
        except ValueError:
            error_msg = (
                loc('errors.invalid_number', min=min_val, max=max_val)
                if loc
                else f'Ошибка: введите число от {min_val} до {max_val}'
            )
            print_wrapped(error_msg, color=Fore.RED)


def get_str_input(
    prompt: str,
    min_length: int = 1,
    validator: Callable[[str], bool] | None = None,
    error_msg: str = 'Ошибка: некорректный ввод',
) -> str:
    """Запросить у пользователя строку с валидацией.

    Args:
        prompt: Приглашение для ввода
        min_length: Минимальная длина строки
        validator: Дополнительная функция-валидатор (возвращает True если OK)
        error_msg: Сообщение об ошибке при некорректном вводе

    Returns:
        Корректно введённая строка
    """
    while True:
        raw = input(f'{Fore.CYAN}{prompt}{Style.RESET_ALL}')
        value = raw.strip()

        if len(value) < min_length:
            print_wrapped(
                f'Ошибка: минимум {min_length} символа(ов)',
                color=Fore.RED,
            )
            continue

        if validator is not None and not validator(value):
            print_wrapped(error_msg, color=Fore.RED)
            continue

        return value