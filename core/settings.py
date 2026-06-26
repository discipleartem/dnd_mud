"""Загрузка и сохранение настроек пользователя.

Настройки хранятся в JSON-файле database/core/settings.json.
"""

import json
from pathlib import Path
from typing import Any

from core.io import load_json
from core.types import LanguageCode, RuntimeSettings

SETTINGS_PATH = Path("database/core/settings.json")
DEFAULT_LANGUAGE: LanguageCode = "ru"
SCHEMA_VERSION = 1


def _default_settings_file() -> dict[str, Any]:
    """Вернуть содержимое settings.json по умолчанию."""
    return {
        "schema_version": SCHEMA_VERSION,
        "language": DEFAULT_LANGUAGE,
    }


def _parse_language(value: object) -> LanguageCode:
    """Извлечь код языка из JSON."""
    if value == "en":
        return "en"
    return "ru"


def _runtime_settings(data: dict[str, Any]) -> RuntimeSettings:
    """Извлечь настройки для runtime."""
    return {
        "language": _parse_language(data.get("language", DEFAULT_LANGUAGE)),
    }


def load_settings() -> RuntimeSettings:
    """Загрузить настройки из JSON-файла.

    Returns:
        Runtime-настройки: language
    """
    if not SETTINGS_PATH.exists():
        return _runtime_settings(_default_settings_file())

    data = load_json(SETTINGS_PATH, _default_settings_file())
    return _runtime_settings(data)


def _write_settings(data: dict[str, Any]) -> None:
    """Записать настройки в JSON-файл."""
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_settings(language: LanguageCode) -> None:
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
