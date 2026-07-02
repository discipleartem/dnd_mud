"""Загрузка предысторий из YAML."""

from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog
from core.grants import grants_from_entity, grants_of_type
from core.localization import resolve_localized_text

BACKGROUNDS_FILE = Path("database/backgrounds/backgrounds.yaml")


def _load_backgrounds_yaml() -> dict[str, Any]:
    """Загрузить данные предысторий."""
    return load_catalog(BACKGROUNDS_FILE, "backgrounds")


def _background_info(background_id: str) -> dict[str, Any]:
    """Сырые данные предыстории."""
    info = _load_backgrounds_yaml().get(background_id, {})
    if isinstance(info, dict):
        return info
    return {}


def _background_grants(background_id: str) -> list[dict[str, Any]]:
    """Grants предыстории."""
    return grants_from_entity(_background_info(background_id))


def _normalize_background(
    background_id: str, info: dict[str, Any], language: str
) -> dict[str, Any]:
    """Локализовать поля одной предыстории."""
    result = dict(info)
    result["id"] = background_id
    result["name"] = resolve_localized_text(info.get("name", {}), language)
    result["description"] = resolve_localized_text(
        info.get("description", {}), language
    )
    feature = info.get("feature", {})
    if isinstance(feature, dict):
        result["feature"] = {
            "name": resolve_localized_text(feature.get("name", {}), language),
            "description": resolve_localized_text(
                feature.get("description", {}), language
            ),
        }
    return result


def load_backgrounds(language: str = "ru") -> list[dict[str, Any]]:
    """Список предысторий для UI."""
    result: list[dict[str, Any]] = []
    for bg_id, info in _load_backgrounds_yaml().items():
        if isinstance(info, dict):
            result.append(_normalize_background(bg_id, info, language))
    return result


def load_background_full(
    background_id: str, language: str = "ru"
) -> dict[str, Any]:
    """Полные данные одной предыстории."""
    info = _background_info(background_id)
    if info:
        return _normalize_background(background_id, info, language)
    return {"id": background_id, "name": background_id}


def get_background_skills(background_id: str) -> list[str]:
    """Два навыка предыстории."""
    skills: list[str] = []
    for grant in grants_of_type(
        _background_grants(background_id), "skill_proficiency"
    ):
        raw = grant.get("skills", [])
        if isinstance(raw, list):
            skills.extend(str(s) for s in raw)
    return skills


def get_background_language_choice(
    background_id: str,
) -> dict[str, Any] | None:
    """Механика выбора языков предыстории или None."""
    for grant in grants_of_type(_background_grants(background_id), "language"):
        if grant.get("choice"):
            count = int(grant.get("count", 0))
            if count > 0:
                return grant
    return None


def get_background_tool_proficiencies(
    background_id: str,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Инструменты предыстории: fixed + choices."""
    fixed: list[str] = []
    choices: list[dict[str, Any]] = []
    for grant in grants_of_type(
        _background_grants(background_id), "tool_proficiency"
    ):
        if grant.get("choice"):
            choices.append(
                {
                    "count": int(grant.get("count", 1)),
                    "pool": str(grant.get("pool", "")),
                }
            )
            continue
        raw = grant.get("tools", [])
        if isinstance(raw, list):
            fixed.extend(str(t) for t in raw)
    return fixed, choices


def _background_inventory_tool_picks(
    background_id: str,
    background_tool_picks: list[str] | None,
) -> list[str]:
    """Инструменты из выбора предыстории, входящие в снаряжение PHB."""
    from core.equipment import resolve_tool_pool

    info = _background_info(background_id)
    pools = info.get("inventory_tool_pools")
    if not isinstance(pools, list) or not pools or not background_tool_picks:
        return []
    allowed: set[str] = set()
    for pool in pools:
        if isinstance(pool, str):
            allowed.update(resolve_tool_pool(pool))
    return [tool_id for tool_id in background_tool_picks if tool_id in allowed]


def get_background_equipment_items(
    background_id: str,
    background_tool_picks: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Предметы стартового снаряжения предыстории (не владения)."""
    from core.inventory import merge_inventory_items, normalize_inventory_item

    items: list[dict[str, Any]] = []
    for grant in grants_of_type(
        _background_grants(background_id), "equipment_item"
    ):
        raw_items = grant.get("items", [])
        if not isinstance(raw_items, list):
            continue
        for entry in raw_items:
            if isinstance(entry, dict):
                normalized = normalize_inventory_item(entry)
                if normalized:
                    items.append(normalized)

    for tool_id in _background_inventory_tool_picks(
        background_id, background_tool_picks
    ):
        items.append({"kind": "tool", "id": tool_id, "qty": 1})

    return merge_inventory_items(items)
