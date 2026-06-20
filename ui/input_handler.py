"""Ввод от пользователя с проверкой и повторным запросом при ошибке."""

import locale
import sys
from typing import Any

from colorama import Fore, Style

if sys.platform == "win32":
    locale.setlocale(locale.LC_ALL, "")
    _encoding = "utf-8"
    try:
        sys.stdout.reconfigure(encoding=_encoding)
        sys.stdin.reconfigure(encoding=_encoding)
    except (ValueError, LookupError):
        _encoding = "cp1251"
        try:
            sys.stdout.reconfigure(encoding=_encoding)
            sys.stdin.reconfigure(encoding=_encoding)
        except (ValueError, LookupError):
            pass
else:
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _error(
    strings: dict[str, Any] | None,
    key: str,
    default: str,
    **kwargs: Any,
) -> str:
    """Локализованное сообщение об ошибке или запасной текст."""
    if strings is not None:
        from core.localization import get_string

        result = get_string(strings, key, **kwargs)
        if result != key:
            return result
    return default.format(**kwargs)


def get_int_input(
    prompt: str,
    min_val: int,
    max_val: int,
    strings: dict[str, Any] | None = None,
    *,
    default: int | None = None,
) -> int:
    """Запросить целое число в заданном диапазоне.

    Пустой ввод (Enter) возвращает ``default``, если он задан и в диапазоне.
    """
    while True:
        try:
            raw = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
            if not raw.strip():
                if default is not None and min_val <= default <= max_val:
                    return default
                raise ValueError
            value = int(raw.strip())
            if min_val <= value <= max_val:
                return value
            msg = _error(
                strings,
                "errors.invalid_number",
                "Ошибка: введите число от {min} до {max}",
                min=min_val,
                max=max_val,
            )
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
        except ValueError:
            msg = _error(
                strings,
                "errors.invalid_input",
                "Ошибка: введите число",
                min=min_val,
                max=max_val,
            )
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")


def get_str_input(
    prompt: str,
    min_length: int = 1,
    only_letters: bool = False,
    strings: dict[str, Any] | None = None,
) -> str:
    """Запросить строку минимальной длины."""
    while True:
        raw = input(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
        value = raw.strip()

        if only_letters and not value.isalpha():
            msg = _error(
                strings,
                "character.name_invalid",
                "Ошибка: имя может содержать только буквы",
            )
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
            continue

        if len(value) < min_length:
            msg = _error(
                strings,
                "character.name_empty",
                "Ошибка: минимум {min_length} символа(ов)",
                min_length=min_length,
            )
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
            continue

        return value
