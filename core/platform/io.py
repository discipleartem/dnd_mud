"""Общие функции чтения YAML и JSON из файловой системы."""

import json
import logging
from pathlib import Path
from typing import Any, Literal

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


def load_file(
    path: Path,
    format: Literal["yaml", "json"],
    default: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Универсальная загрузка YAML или JSON файла.

    Args:
        path: Путь к файлу
        format: Формат файла ("yaml" или "json")
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
            if format == "yaml":
                data = yaml.safe_load(f) or {}
            else:
                data = json.load(f)
        if isinstance(data, dict):
            return data
        if strict:
            raise CatalogLoadError(
                f"Ожидался объект {format.upper()} в корне файла: {path}"
            )
    except CatalogLoadError:
        raise
    except (yaml.YAMLError, json.JSONDecodeError, OSError) as exc:
        if strict:
            logger.warning("Битый %s: %s", format, path)
            raise CatalogLoadError(
                f"Не удалось прочитать {format}: {path}"
            ) from exc
    return fallback.copy()


def load_yaml(
    path: Path,
    default: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Загрузить YAML-файл."""
    return load_file(path, "yaml", default, strict=strict)


def load_json(
    path: Path,
    default: dict[str, Any] | None = None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    """Загрузить JSON-файл."""
    return load_file(path, "json", default, strict=strict)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Записать словарь в JSON-файл."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
