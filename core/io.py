"""Общие функции чтения YAML и JSON из файловой системы."""

import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class CatalogLoadError(OSError):
    """Ошибка чтения повреждённого каталога YAML или JSON."""


def merge_unique(*parts: list[str]) -> list[str]:
    """Объединить списки строк без дублей, сохраняя порядок."""
    result: list[str] = []
    for part in parts:
        for item in part:
            if item not in result:
                result.append(item)
    return result


def load_yaml(
    path: Path,
    default: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Загрузить YAML-файл.

    Args:
        path: Путь к файлу
        default: Значение при отсутствии файла
        strict: При True — исключение на битом файле (каталоги игры)

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
        if strict:
            raise CatalogLoadError(
                f"Ожидался объект YAML в корне файла: {path}"
            )
    except CatalogLoadError:
        raise
    except (yaml.YAMLError, OSError) as exc:
        if strict:
            logger.warning("Битый YAML-каталог: %s", path)
            raise CatalogLoadError(
                f"Не удалось прочитать YAML: {path}"
            ) from exc
    return fallback.copy()


def load_json(
    path: Path,
    default: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Загрузить JSON-файл.

    Args:
        path: Путь к файлу
        default: Значение при отсутствии файла
        strict: При True — исключение на битом файле

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
        if strict:
            raise CatalogLoadError(
                f"Ожидался объект JSON в корне файла: {path}"
            )
    except CatalogLoadError:
        raise
    except (json.JSONDecodeError, OSError) as exc:
        if strict:
            logger.warning("Битый JSON: %s", path)
            raise CatalogLoadError(
                f"Не удалось прочитать JSON: {path}"
            ) from exc
    return fallback.copy()


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Записать словарь в JSON-файл."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
