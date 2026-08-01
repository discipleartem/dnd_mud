"""Загрузка YAML-каталогов с overlay модов."""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.platform.io import CatalogLoadError, load_json, load_yaml
from core.types import GameDifficulty

logger = logging.getLogger(__name__)

MODS_DIR = Path("mods")
MODS_STATE_FILE = Path("database/core/mods_state.json")

_mod_gating_difficulty: GameDifficulty | None = None


def set_mod_gating_difficulty(difficulty: GameDifficulty | None) -> None:
    """Режим для фильтрации модов с ``requires_game_difficulty``."""
    global _mod_gating_difficulty
    _mod_gating_difficulty = difficulty


def get_mod_gating_difficulty() -> GameDifficulty | None:
    """Текущий режим gating модов (None — без фильтра по сложности)."""
    return _mod_gating_difficulty


def _mod_allowed_for_difficulty(
    manifest: dict[str, Any],
    difficulty: GameDifficulty | None,
) -> bool:
    """Мод доступен при текущем режиме сложности."""
    required = manifest.get("requires_game_difficulty")
    if required is None:
        return True
    if difficulty is None:
        return True
    if isinstance(required, str):
        return difficulty == required
    if isinstance(required, list):
        return difficulty in [str(item) for item in required]
    return True


def _mod_id_list(manifest: dict[str, Any], key: str) -> list[str]:
    """Список ID модов из поля manifest (строка или список)."""
    raw = manifest.get(key)
    if raw is None:
        return []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return []


def mod_enable_error(
    mod_id: str,
    *,
    enabled_ids: frozenset[str] | None = None,
) -> dict[str, str] | None:
    """Проверить, можно ли включить мод. None — ок; иначе payload для UI."""
    if enabled_ids is None:
        enabled_ids = get_enabled_mod_ids()
    manifest = _load_mod_manifest(mod_id)
    if not manifest:
        return {"key": "mods.error_missing", "mod_id": mod_id}

    candidate = frozenset(enabled_ids | {mod_id})

    for required in _mod_id_list(manifest, "requires"):
        if required not in candidate:
            return {
                "key": "mods.error_requires",
                "mod_id": mod_id,
                "other_mod_id": required,
            }

    for conflict in _mod_id_list(manifest, "conflicts"):
        if conflict in candidate and conflict != mod_id:
            return {
                "key": "mods.error_conflicts",
                "mod_id": mod_id,
                "other_mod_id": conflict,
            }

    for other_id in candidate:
        if other_id == mod_id:
            continue
        other_manifest = _load_mod_manifest(other_id)
        if mod_id in _mod_id_list(other_manifest, "conflicts"):
            return {
                "key": "mods.error_conflicts",
                "mod_id": mod_id,
                "other_mod_id": other_id,
            }

    return None


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


def _apply_overlay_actions(
    data: dict[str, Any],
    overlay: dict[str, Any],
) -> dict[str, Any]:
    """delete / replace_entity, затем deep-merge остального overlay."""
    result = dict(data)

    delete_spec = overlay.get("delete")
    if isinstance(delete_spec, dict):
        for section, entity_ids in delete_spec.items():
            section_data = result.get(section)
            if not isinstance(section_data, dict):
                continue
            if not isinstance(entity_ids, list):
                continue
            for entity_id in entity_ids:
                section_data.pop(str(entity_id), None)

    replace_spec = overlay.get("replace_entity")
    if isinstance(replace_spec, dict):
        for section, entities in replace_spec.items():
            section_data = result.get(section)
            if not isinstance(section_data, dict):
                continue
            if not isinstance(entities, dict):
                continue
            for entity_id, entity_data in entities.items():
                section_data[str(entity_id)] = entity_data

    remainder = {
        key: value
        for key, value in overlay.items()
        if key not in ("delete", "replace_entity")
    }
    merged = _deep_merge(result, remainder)
    if isinstance(merged, dict):
        return merged
    return result


def get_enabled_mod_ids() -> frozenset[str]:
    """ID модов, включённых в ``mods_state.json`` (без gating overlay)."""
    state = load_json(MODS_STATE_FILE, default={"enabled": []})
    enabled = state.get("enabled", [])
    if isinstance(enabled, list):
        return frozenset(str(item) for item in enabled)
    return frozenset()


def _enabled_mod_ids(
    *,
    game_difficulty: GameDifficulty | None = None,
) -> list[str]:
    """ID включённых модов из mods_state.json с учётом gating."""
    state = load_json(MODS_STATE_FILE, default={"enabled": []})
    enabled = state.get("enabled", [])
    if not isinstance(enabled, list):
        return []
    difficulty = (
        game_difficulty
        if game_difficulty is not None
        else _mod_gating_difficulty
    )
    result: list[str] = []
    for mod_id in enabled:
        mod_key = str(mod_id)
        manifest = _load_mod_manifest(mod_key)
        if _mod_allowed_for_difficulty(manifest, difficulty):
            result.append(mod_key)
    return result


def _mod_manifest_path(mod_id: str) -> Path:
    """Путь к manifest.yaml мода."""
    return MODS_DIR / mod_id / "manifest.yaml"


def _load_mod_manifest(mod_id: str) -> dict[str, Any]:
    """Загрузить manifest мода; битый файл — пустой dict."""
    try:
        return load_yaml(_mod_manifest_path(mod_id), strict=True)
    except CatalogLoadError:
        logger.warning("Битый manifest мода %s, overlay пропущен", mod_id)
        return {}


def _apply_mod_overlays(
    data: dict[str, Any],
    target_path: Path,
    *,
    game_difficulty: GameDifficulty | None = None,
) -> dict[str, Any]:
    """Применить overlay всех включённых модов к данным файла."""
    target = str(target_path).replace("\\", "/")
    result = dict(data)
    for mod_id in _enabled_mod_ids(game_difficulty=game_difficulty):
        manifest = _load_mod_manifest(mod_id)
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
                result = _apply_overlay_actions(result, overlay_data)
    return result


def load_merged_yaml(
    path: Path,
    *,
    game_difficulty: GameDifficulty | None = None,
) -> dict[str, Any]:
    """Загрузить YAML с deep-merge overlay включённых модов."""
    data = load_yaml(path, strict=True)
    return _apply_mod_overlays(data, path, game_difficulty=game_difficulty)


def list_available_mods() -> list[dict[str, Any]]:
    """Манифесты всех модов в ``mods/``."""
    result: list[dict[str, Any]] = []
    if not MODS_DIR.exists():
        return result
    for path in sorted(MODS_DIR.iterdir()):
        if not path.is_dir():
            continue
        manifest = _load_mod_manifest(path.name)
        if manifest:
            entry = dict(manifest)
            entry.setdefault("id", path.name)
            result.append(entry)
    return result


def set_mod_enabled(mod_id: str, enabled: bool) -> dict[str, str] | None:
    """Включить или выключить мод в ``mods_state.json``.

    Returns:
        Payload ошибки для UI или None при успехе.
    """
    state = load_json(MODS_STATE_FILE, default={"enabled": []})
    current = state.get("enabled", [])
    if not isinstance(current, list):
        current = []
    enabled_ids = frozenset(str(item) for item in current)

    if enabled:
        error = mod_enable_error(mod_id, enabled_ids=enabled_ids)
        if error is not None:
            return error

    enabled_list = [str(item) for item in current]
    if enabled and mod_id not in enabled_list:
        enabled_list.append(mod_id)
    elif not enabled and mod_id in enabled_list:
        enabled_list.remove(mod_id)
    save_mods_state(enabled_list)
    return None


def save_mods_state(enabled_ids: list[str]) -> None:
    """Сохранить список включённых модов."""
    from core.platform.io import save_json

    save_json(MODS_STATE_FILE, {"enabled": enabled_ids})


def clear_mod_loader_cache() -> None:
    """Сбросить кэш загрузчиков каталогов (для тестов)."""
    load_merged_catalog.cache_clear()


@lru_cache(maxsize=32)
def load_merged_catalog(
    path_str: str,
    catalog_key: str,
    game_difficulty: GameDifficulty | None = None,
) -> dict[str, Any]:
    """Загрузить словарь каталога (races, classes, …) с модами."""
    path = Path(path_str)
    data = load_merged_yaml(path, game_difficulty=game_difficulty)
    catalog = data.get(catalog_key, {})
    if isinstance(catalog, dict):
        return catalog
    return {}
