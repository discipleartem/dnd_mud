"""Стартовое снаряжение предыстории."""

from core.catalogs.backgrounds import (
    background_grants,
    background_info,
)
from core.catalogs.equipment import resolve_tool_pool
from core.grants.normalize import grants_of_type
from core.inventory.items import (
    merge_inventory_items,
    normalize_inventory_item,
)
from core.types import InventoryItem


def _background_inventory_tool_picks(
    background_id: str,
    background_tool_picks: list[str] | None,
) -> list[str]:
    """Инструменты из выбора предыстории, входящие в снаряжение PHB."""
    info = background_info(background_id)
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
) -> list[InventoryItem]:
    """Предметы стартового снаряжения предыстории (не владения)."""
    items: list[InventoryItem] = []
    for grant in grants_of_type(
        background_grants(background_id), "equipment_item"
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


__all__ = ["get_background_equipment_items"]
