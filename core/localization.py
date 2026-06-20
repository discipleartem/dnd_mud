"""Загрузка и получение строк интерфейса на разных языках.

Строки хранятся в YAML-файлах в папке database/strings/.
Язык по умолчанию — русский, если нет — английский (запасной).
"""

from pathlib import Path
from typing import Any

from core.io import load_yaml

STRINGS_DIR = Path("database/strings")


def load_strings(language: str) -> dict[str, Any]:
    """Загрузить строки для указанного языка.

    Сначала пытается загрузить файл language.yaml.
    Если его нет — загружает en.yaml как запасной вариант.

    Args:
        language: Код языка ('ru', 'en' и т.д.)

    Returns:
        Словарь со строками
    """
    strings_path = STRINGS_DIR / f"{language}.yaml"
    fallback_path = STRINGS_DIR / "en.yaml"

    strings = load_yaml(strings_path)
    fallback = load_yaml(fallback_path)

    result = fallback.copy()
    result.update(strings)
    return result


def get_string(strings: dict[str, Any], key: str, **kwargs: Any) -> str:
    """Получить строку по ключу с поддержкой вложенности через точку.

    Пример:
        get_string(strings, "menu.new_game")  # -> "Новая игра"
        get_string(
            strings, "info.welcome", name="Томас"
        )  # -> "Привет, Томас!"

    Args:
        strings: Словарь со строками
        key: Ключ вида "menu.new_game"
        **kwargs: Параметры для подстановки в строку

    Returns:
        Строка или ключ, если строка не найдена
    """
    parts = key.split(".")

    value: Any = strings
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return key

    if value is None:
        return key

    if not isinstance(value, str):
        return str(value)

    if kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value
