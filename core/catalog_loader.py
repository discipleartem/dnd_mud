"""Единая загрузка YAML-каталогов с mod overlay."""

from functools import lru_cache
from pathlib import Path
from typing import Any

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
    from core.abilities import _load_abilities_yaml, _load_skills_yaml
    from core.backgrounds import _load_backgrounds_yaml
    from core.classes import _load_classes_yaml
    from core.constants import _load_constants
    from core.equipment import (
        _load_armor,
        _load_equipment_items,
        _load_tools,
        _load_weapons,
    )
    from core.feats_loader import _load_feats_yaml
    from core.languages import _load_languages_yaml
    from core.localization import clear_strings_cache
    from core.races import _load_races_yaml

    for loader in (
        _load_races_yaml,
        _load_backgrounds_yaml,
        _load_classes_yaml,
        _load_feats_yaml,
        _load_languages_yaml,
        _load_abilities_yaml,
        _load_skills_yaml,
        _load_constants,
        _load_weapons,
        _load_armor,
        _load_tools,
        _load_equipment_items,
    ):
        loader.cache_clear()
    clear_strings_cache()
