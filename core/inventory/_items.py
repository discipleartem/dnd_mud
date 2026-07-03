"""Нормализация и слияние записей инвентаря."""

from typing import Any, Literal

from core.equipment import load_equipment_item

ItemKind = Literal["weapon", "armor", "tool", "equipment"]


def normalize_inventory_item(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Нормализовать запись инвентаря."""
    kind = raw.get("kind")
    item_id = raw.get("id")
    if kind not in ("weapon", "armor", "tool", "equipment"):
        return None
    if not isinstance(item_id, str) or not item_id:
        return None
    qty_raw = raw.get("qty", 1)
    qty = int(qty_raw) if isinstance(qty_raw, int) else 1
    if qty < 1:
        qty = 1
    return {"kind": kind, "id": item_id, "qty": qty}


def expand_pack_contents(item_id: str) -> list[dict[str, Any]]:
    """Развернуть набор (pack) в список предметов."""
    info = load_equipment_item(item_id)
    if info.get("category") != "pack":
        return []
    contents = info.get("contents", [])
    if not isinstance(contents, list):
        return []
    result: list[dict[str, Any]] = []
    for entry in contents:
        if not isinstance(entry, dict):
            continue
        normalized = normalize_inventory_item(entry)
        if normalized:
            result.append(normalized)
    return result


def merge_inventory_items(
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Сложить одинаковые предметы по kind+id."""
    merged: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for raw in items:
        item = normalize_inventory_item(raw) if "kind" in raw else None
        if item is None:
            continue
        key = (str(item["kind"]), str(item["id"]))
        if key not in merged:
            order.append(key)
            merged[key] = 0
        merged[key] += int(item["qty"])
    return [
        {"kind": kind, "id": item_id, "qty": merged[(kind, item_id)]}
        for kind, item_id in order
    ]


def add_items_to_inventory(
    inventory: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Добавить предметы в инвентарь с развёрткой наборов."""
    expanded: list[dict[str, Any]] = list(inventory)
    for raw in new_items:
        item = normalize_inventory_item(raw)
        if item is None:
            continue
        if (
            item["kind"] == "equipment"
            and load_equipment_item(item["id"]).get("category") == "pack"
        ):
            expanded.extend(expand_pack_contents(item["id"]))
        else:
            expanded.append(item)
    return merge_inventory_items(expanded)


def inventory_item_quantity(
    inventory: list[dict[str, Any]], kind: str, item_id: str
) -> int:
    """Суммарное количество предмета kind+id в инвентаре."""
    total = 0
    for item in inventory:
        if item.get("kind") == kind and item.get("id") == item_id:
            total += int(item.get("qty", 1))
    return total


def _equipped_item_counts(
    equipped: dict[str, Any],
) -> dict[tuple[str, str], int]:
    """Сколько предметов каждого kind+id занято экипировкой."""
    counts: dict[tuple[str, str], int] = {}
    armor_id = equipped.get("armor")
    if isinstance(armor_id, str) and armor_id:
        key = ("armor", armor_id)
        counts[key] = counts.get(key, 0) + 1
    if equipped.get("shield"):
        key = ("armor", "shield")
        counts[key] = counts.get(key, 0) + 1
    main_hand = equipped.get("main_hand")
    if isinstance(main_hand, str) and main_hand:
        key = ("weapon", main_hand)
        counts[key] = counts.get(key, 0) + 1
    off_hand = equipped.get("off_hand")
    if isinstance(off_hand, str) and off_hand:
        key = ("weapon", off_hand)
        counts[key] = counts.get(key, 0) + 1
    return counts


def inventory_excluding_equipped(
    inventory: list[dict[str, Any]],
    equipped: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Инвентарь для UI: без экипированного; save не меняется."""
    if not equipped:
        return list(inventory)
    hidden = _equipped_item_counts(equipped)
    if not hidden:
        return list(inventory)
    visible: list[dict[str, Any]] = []
    for item in inventory:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        remaining = qty - hidden.get((kind, item_id), 0)
        if remaining > 0:
            visible.append({"kind": kind, "id": item_id, "qty": remaining})
    return visible
