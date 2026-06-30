"""Единая загрузка YAML-каталогов с mod overlay."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.localization import clear_strings_cache
from core.mod_loader import clear_mod_loader_cache, load_merged_catalog


@lru_cache(maxsize=32)
def load_catalog(path: Path | str, root_key: str) -> dict[str, Any]:
    """Загрузить словарь каталога из YAML (с deep-merge модов)."""
    return load_merged_catalog(str(path), root_key)


def clear_catalog_cache() -> None:
    """Сбросить кэш каталогов и mod loader (для тестов)."""
    load_catalog.cache_clear()
    clear_mod_loader_cache()


def clear_all_catalog_caches() -> None:
    """Сбросить все кэши загрузчиков каталогов и строк (для тестов)."""
    clear_catalog_cache()
    clear_strings_cache()
