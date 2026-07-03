"""Единая загрузка YAML-каталогов с mod overlay."""

from pathlib import Path
from typing import Any

from core.localization import clear_strings_cache
from core.mod_loader import (
    clear_mod_loader_cache,
    get_mod_gating_difficulty,
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
    clear_catalog_cache()
    clear_strings_cache()


def reload_catalogs() -> None:
    """Перезагрузить каталоги и строки без рестарта интерпретатора."""
    clear_all_catalog_caches()
