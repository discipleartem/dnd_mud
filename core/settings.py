"""Загрузка и сохранение настроек пользователя.

Настройки хранятся в JSON-файле database/core/settings.json.
"""

import json
from pathlib import Path
from typing import Any

from core.io import load_json

SETTINGS_PATH = Path("database/core/settings.json")
DEFAULT_LANGUAGE = "ru"
SCHEMA_VERSION = 1


def _default_settings() -> dict[str, Any]:
    """Вернуть настройки по умолчанию."""
    return {
        "schema_version": SCHEMA_VERSION,
        "language": DEFAULT_LANGUAGE,
    }


def _runtime_settings(data: dict[str, Any]) -> dict[str, Any]:
    """Извлечь настройки для runtime."""
    defaults = _default_settings()
    return {
        "language": data.get("language", defaults["language"]),
    }


def load_settings() -> dict[str, Any]:
    """Загрузить настройки из JSON-файла.

    Returns:
        Словарь с настройками: language
    """
    if not SETTINGS_PATH.exists():
        return _runtime_settings(_default_settings())

    data = load_json(SETTINGS_PATH, _default_settings())
    return _runtime_settings(data)


def _write_settings(data: dict[str, Any]) -> None:
    """Записать настройки в JSON-файл."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_settings(language: str) -> None:
    """Сохранить настройки в JSON-файл.

    Args:
        language: Код языка ('ru', 'en')
    """
    _write_settings(
        {
            "schema_version": SCHEMA_VERSION,
            "language": language,
        }
    )
