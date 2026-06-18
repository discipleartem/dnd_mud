"""Загрузка и получение строк интерфейса на разных языках.

Строки хранятся в YAML-файлах в папке database/strings/.
Язык по умолчанию — русский, если нет — английский (запасной).
"""

from pathlib import Path

import yaml

STRINGS_DIR = Path("database/strings")


def load_strings(language: str) -> dict:
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

    strings = {}
    fallback = {}

    if strings_path.exists():
        with open(strings_path, encoding="utf-8") as f:
            strings = yaml.safe_load(f) or {}

    if fallback_path.exists():
        with open(fallback_path, encoding="utf-8") as f:
            fallback = yaml.safe_load(f) or {}

    # Склеиваем: свои строки поверх запасных
    result = fallback.copy()
    result.update(strings)
    return result


def get_string(strings: dict, key: str, **kwargs) -> str:
    """Получить строку по ключу с поддержкой вложенности через точку.

    Пример:
        get_string(strings, "menu.new_game")  # -> "Новая игра"
        get_string(strings, "info.welcome", name="Томас")  # -> "Привет, Томас!"

    Args:
        strings: Словарь со строками
        key: Ключ вида "menu.new_game"
        **kwargs: Параметры для подстановки в строку

    Returns:
        Строка или ключ, если строка не найдена
    """
    parts = key.split(".")

    # Ищем значение во вложенном словаре
    value = strings
    for part in parts:
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return key

    # Если нашли не строку — возвращаем как есть
    if not isinstance(value, str):
        return str(value) if value is not None else key

    # Подставляем параметры, если нужно
    if kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value