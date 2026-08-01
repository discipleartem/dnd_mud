"""Единая загрузка YAML-каталогов с mod overlay."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from core.platform.catalog_session import (
    get_catalog_session,
    get_mod_gating_difficulty,
)
from core.platform.localization import resolve_localized_text
from core.platform.mod_loader import (
    clear_mod_loader_cache,
    load_merged_catalog,
)


def load_catalog(path: Path | str, root_key: str) -> dict[str, Any]:
    """Загрузить словарь каталога из YAML (с deep-merge модов)."""
    return load_merged_catalog(
        str(path),
        root_key,
        game_difficulty=get_mod_gating_difficulty(),
    )


def clear_catalog_cache() -> None:
    """Сбросить кэш каталогов (для тестов)."""
    clear_mod_loader_cache()


def clear_all_catalog_caches() -> None:
    """Сбросить все кэши загрузчиков каталогов и строк (для тестов)."""
    get_catalog_session().clear_caches()


def reload_catalogs() -> None:
    """Перезагрузить каталоги и строки без рестарта интерпретатора."""
    get_catalog_session().clear_caches()


def load_catalog_items(
    catalog_data: dict[str, Any],
    language: str,
    item_id_key: str = "id",
    name_key: str = "name",
    fallback: Callable[[str, str], str] | None = None,
) -> list[dict[str, Any]]:
    """Универсальный загрузчик элементов каталога с локализацией.

    Args:
        catalog_data: Словарь с данными каталога
        language: Код языка для локализации
        item_id_key: Ключ для ID элемента (по умолчанию "id")
        name_key: Ключ для локализуемого имени (по умолчанию "name")
        fallback: Функция для fallback значения имени

    Returns:
        Список словарей с id и локализованными именами
    """
    result: list[dict[str, Any]] = []
    for item_id, item_info in catalog_data.items():
        if not isinstance(item_info, dict):
            continue
        name = item_info.get(name_key, item_id)
        if fallback:
            localized_name = fallback(name, language)
        else:
            localized_name = resolve_localized_text(
                name, language, fallback=item_id
            )
        result.append({item_id_key: item_id, name_key: localized_name})
    return result
