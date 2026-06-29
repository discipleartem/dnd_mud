"""Загрузка YAML-каталогов с overlay модов."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_json, load_yaml

MODS_DIR = Path("mods")
MODS_STATE_FILE = Path("database/core/mods_state.json")


def _deep_merge(base: Any, overlay: Any) -> Any:
    """Рекурсивно объединить overlay в base."""
    if not isinstance(base, dict) or not isinstance(overlay, dict):
        return overlay
    result = dict(base)
    for key, value in overlay.items():
        if key in result:
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _enabled_mod_ids() -> list[str]:
    """ID включённых модов из mods_state.json."""
    state = load_json(MODS_STATE_FILE, default={"enabled": []})
    enabled = state.get("enabled", [])
    if isinstance(enabled, list):
        return [str(mod_id) for mod_id in enabled]
    return []


def _mod_manifest_path(mod_id: str) -> Path:
    """Путь к manifest.yaml мода."""
    return MODS_DIR / mod_id / "manifest.yaml"


def _apply_mod_overlays(
    data: dict[str, Any], target_path: Path
) -> dict[str, Any]:
    """Применить overlay всех включённых модов к данным файла."""
    target = str(target_path).replace("\\", "/")
    result = dict(data)
    for mod_id in _enabled_mod_ids():
        manifest = load_yaml(_mod_manifest_path(mod_id))
        overlays = manifest.get("overlays", [])
        if not isinstance(overlays, list):
            continue
        for entry in overlays:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("target", "")).replace("\\", "/") != target:
                continue
            overlay_path = MODS_DIR / mod_id / str(entry.get("path", ""))
            if not overlay_path.exists():
                continue
            overlay_data = load_yaml(overlay_path)
            if isinstance(overlay_data, dict):
                result = _deep_merge(result, overlay_data)
    return result


def load_merged_yaml(path: Path) -> dict[str, Any]:
    """Загрузить YAML с deep-merge overlay включённых модов."""
    data = load_yaml(path)
    return _apply_mod_overlays(data, path)


def clear_mod_loader_cache() -> None:
    """Сбросить кэш загрузчиков каталогов (для тестов)."""
    load_merged_catalog.cache_clear()


@lru_cache(maxsize=16)
def load_merged_catalog(path_str: str, catalog_key: str) -> dict[str, Any]:
    """Загрузить словарь каталога (races, classes, …) с модами."""
    path = Path(path_str)
    data = load_merged_yaml(path)
    catalog = data.get(catalog_key, {})
    if isinstance(catalog, dict):
        return catalog
    return {}
