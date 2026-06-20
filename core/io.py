"""Общие функции чтения YAML и JSON из файловой системы."""

import json
from pathlib import Path
from typing import Any

import yaml


def load_yaml(
    path: Path, default: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Загрузить YAML-файл.

    Args:
        path: Путь к файлу
        default: Значение при отсутствии файла или ошибке чтения

    Returns:
        Словарь из файла или default (пустой dict, если default не задан)
    """
    fallback = default if default is not None else {}
    if not path.exists():
        return fallback.copy()
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if isinstance(data, dict):
            return data
    except (yaml.YAMLError, OSError):
        pass
    return fallback.copy()


def load_json(
    path: Path, default: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Загрузить JSON-файл.

    Args:
        path: Путь к файлу
        default: Значение при отсутствии файла или ошибке чтения

    Returns:
        Словарь из файла или default (пустой dict, если default не задан)
    """
    fallback = default if default is not None else {}
    if not path.exists():
        return fallback.copy()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return fallback.copy()
