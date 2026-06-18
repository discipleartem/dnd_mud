"""Загрузка и сохранение настроек пользователя.

Настройки хранятся в YAML-файле database/settings.yaml.
"""

from pathlib import Path
from typing import Any

import yaml

SETTINGS_PATH = Path("database/core/settings.yaml")
DEFAULT_LANGUAGE = "ru"


def load_settings() -> dict[str, Any]:
    """Загрузить настройки из YAML-файла.

    Настройки хранятся в YAML-файле database/core/settings.yaml.

    Returns:
        Словарь с настройками: {"language": "ru", "hardcore": False}
    """
    if not SETTINGS_PATH.exists():
        return {"language": DEFAULT_LANGUAGE, "hardcore": False}

    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return {
            "language": data.get("language", DEFAULT_LANGUAGE),
            "hardcore": data.get("hardcore", False),
        }
    except (yaml.YAMLError, OSError):
        return {"language": DEFAULT_LANGUAGE, "hardcore": False}


def save_settings(language: str, hardcore: bool) -> None:
    """Сохранить настройки в YAML-файл.

    Args:
        language: Код языка ('ru', 'en')
        hardcore: Режим Hard Core
    """
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"language": language, "hardcore": hardcore}
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
