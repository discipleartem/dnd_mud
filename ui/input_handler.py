"""Ввод от пользователя с проверкой и повторным запросом при ошибке."""

import sys
import io

from colorama import Fore, Style

# Устанавливаем UTF-8 кодировку для stdin/stdout
# для корректной работы с кириллицей в терминале
if sys.platform == 'win32':
    import locale
    locale.setlocale(locale.LC_ALL, '')
else:
    sys.stdin = io.TextIOWrapper(
        sys.stdin.buffer,
        encoding='utf-8',
        errors='replace'
    )
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )


def get_choice(options: list[str], prompt: str = "> ") -> int:
    """Показать нумерованный список и получить выбор пользователя.

    Выводит опции с номерами (1, 2, 3...), ждёт ввод числа.
    Если введено неправильное число — просит повторить.

    Args:
        options: Список строк-опций
        prompt: Текст перед полем ввода

    Returns:
        Номер выбранной опции (1, 2, 3...)
    """
    for i, option in enumerate(options, start=1):
        print(f"  {Fore.YELLOW}{i}{Style.RESET_ALL}. {option}")

    print()

    while True:
        try:
            raw = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
            value = int(raw.strip())
            if 1 <= value <= len(options):
                return value
            print(
                f"{Fore.RED}Ошибка: введите число от 1 до "
                f"{len(options)}{Style.RESET_ALL}"
            )
        except ValueError:
            print(f"{Fore.RED}Ошибка: введите число{Style.RESET_ALL}")


def get_int_input(prompt: str, min_val: int, max_val: int) -> int:
    """Запросить целое число в заданном диапазоне.

    Args:
        prompt: Текст перед полем ввода
        min_val: Минимальное допустимое значение
        max_val: Максимальное допустимое значение

    Returns:
        Введённое число
    """
    while True:
        try:
            raw = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
            value = int(raw.strip())
            if min_val <= value <= max_val:
                return value
            print(
                f"{Fore.RED}Ошибка: введите число от {min_val} до "
                f"{max_val}{Style.RESET_ALL}"
            )
        except ValueError:
            print(f"{Fore.RED}Ошибка: введите число{Style.RESET_ALL}")


def get_str_input(prompt: str, min_length: int = 1, only_letters: bool = False) -> str:
    """Запросить строку минимальной длины.

    Args:
        prompt: Текст перед полем ввода
        min_length: Минимальное количество символов
        only_letters: Если True, разрешены только буквы (кириллица/латиница)

    Returns:
        Введённая строка (без лишних пробелов по краям)
    """
    while True:
        raw = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
        value = raw.strip()

        if only_letters and not value.isalpha():
            print(
                f"{Fore.RED}Ошибка: имя может содержать только "
                f"буквы (кириллица или латиница){Style.RESET_ALL}"
            )
            continue

        if len(value) < min_length:
            print(
                f"{Fore.RED}Ошибка: минимум {min_length} "
                f"символа(ов){Style.RESET_ALL}"
            )
            continue

        return value
