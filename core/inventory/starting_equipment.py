"""Стартовое снаряжение класса из YAML (resolve и доступность)."""

from typing import Any

from core.catalogs.classes import get_class_dict
from core.catalogs.equipment import (
    all_weapon_ids,
    armor_category,
    armor_strength_requirement,
    resolve_tool_pool,
    weapon_matches_category,
)
from core.inventory.items import (
    add_items_to_inventory,
    normalize_inventory_item,
)
from core.mechanics.proficiencies import (
    has_weapon_pool_proficiency,
    has_weapon_proficiency,
)
from core.types import InventoryItem


def get_class_starting_equipment_config(class_id: str) -> dict[str, Any]:
    """Конфиг стартового снаряжения класса."""
    info = get_class_dict(class_id)
    raw = info.get("starting_equipment", {})
    return dict(raw) if isinstance(raw, dict) else {}


def _option_weapon_items_proficient(
    option: dict[str, Any],
    weapon_proficiencies: list[str],
) -> bool:
    """Владение всем оружием из items опции (например warhammer у дварфа)."""
    raw_items = option.get("items", [])
    if not isinstance(raw_items, list):
        return False
    weapon_ids = [
        str(entry.get("id", ""))
        for entry in raw_items
        if isinstance(entry, dict) and entry.get("kind") == "weapon"
    ]
    if not weapon_ids:
        return False
    return all(
        has_weapon_proficiency(weapon_proficiencies, weapon_id)
        for weapon_id in weapon_ids
    )


def _option_available(
    option: dict[str, Any],
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
) -> bool:
    """Доступна ли опция по владениям."""
    req_armor = option.get("requires_armor")
    if isinstance(req_armor, str) and req_armor not in armor_proficiencies:
        return False
    req_weapon = option.get("requires_weapon_pool")
    if isinstance(req_weapon, str):
        pool_ok = has_weapon_pool_proficiency(req_weapon, weapon_proficiencies)
        item_ok = _option_weapon_items_proficient(option, weapon_proficiencies)
        if not pool_ok and not item_ok:
            return False
    return True


def all_weapons_in_pool(pool: str) -> list[str]:
    """Все виды оружия из пула категории."""
    return sorted(
        weapon_id
        for weapon_id in all_weapon_ids()
        if weapon_matches_category(pool, weapon_id)
    )


def weapons_for_pool(
    pool: str,
    weapon_proficiencies: list[str],
) -> list[str]:
    """Оружие из пула, доступное по владению."""
    return [
        weapon_id
        for weapon_id in all_weapons_in_pool(pool)
        if has_weapon_proficiency(weapon_proficiencies, weapon_id)
    ]


def tools_for_pool(pool: str) -> list[str]:
    """Инструменты из пула."""
    return sorted(resolve_tool_pool(pool))


def list_equipment_choices(class_id: str) -> list[dict[str, Any]]:
    """Группы выбора стартового снаряжения."""
    config = get_class_starting_equipment_config(class_id)
    choices = config.get("choices", [])
    if isinstance(choices, list):
        return [dict(c) for c in choices if isinstance(c, dict)]
    return []


def list_fixed_items(class_id: str) -> list[dict[str, Any]]:
    """Фиксированные предметы класса."""
    config = get_class_starting_equipment_config(class_id)
    fixed = config.get("fixed", [])
    if isinstance(fixed, list):
        return [dict(item) for item in fixed if isinstance(item, dict)]
    return []


def _items_from_option(
    option: dict[str, Any],
    choices: dict[str, str],
    choice_id: str,
) -> list[InventoryItem]:
    """Собрать предметы из выбранной опции."""
    items: list[InventoryItem] = []
    raw_items = option.get("items", [])
    if isinstance(raw_items, list):
        for entry in raw_items:
            if isinstance(entry, dict):
                normalized = normalize_inventory_item(entry)
                if normalized:
                    items.append(normalized)
    weapon_picks = option.get("weapon_picks", [])
    if isinstance(weapon_picks, list):
        for idx, pick in enumerate(weapon_picks):
            if not isinstance(pick, dict):
                continue
            pool = str(pick.get("pool", ""))
            key = f"{choice_id}_weapon_{idx}"
            weapon_id = choices.get(key)
            if weapon_id and weapon_matches_category(pool, weapon_id):
                items.append({"kind": "weapon", "id": weapon_id, "qty": 1})
    tool_picks = option.get("tool_picks", [])
    if isinstance(tool_picks, list):
        for idx, pick in enumerate(tool_picks):
            if not isinstance(pick, dict):
                continue
            pool = str(pick.get("pool", ""))
            key = f"{choice_id}_tool_{idx}"
            tool_id = choices.get(key)
            if tool_id and tool_id in tools_for_pool(pool):
                items.append({"kind": "tool", "id": tool_id, "qty": 1})
    return items


def resolve_starting_items(
    class_id: str,
    choices: dict[str, str],
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
) -> list[InventoryItem]:
    """Разрешить стартовое снаряжение класса в список предметов."""
    inventory: list[InventoryItem] = []
    for fixed in list_fixed_items(class_id):
        normalized = normalize_inventory_item(fixed)
        if normalized:
            inventory.append(normalized)
    for choice_group in list_equipment_choices(class_id):
        choice_id = str(choice_group.get("id", ""))
        if not choice_id:
            continue
        option_id = choices.get(choice_id)
        if not option_id:
            continue
        options = choice_group.get("options", [])
        if not isinstance(options, list):
            continue
        selected: dict[str, Any] | None = None
        for option in options:
            if not isinstance(option, dict):
                continue
            if str(option.get("id", "")) != option_id:
                continue
            if _option_available(
                option, weapon_proficiencies, armor_proficiencies
            ):
                selected = option
                break
        if selected is None:
            continue
        inventory.extend(
            _items_from_option(
                selected,
                choices,
                choice_id,
            )
        )
    return add_items_to_inventory([], inventory)


def equipment_option_available(
    option: dict[str, Any],
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
) -> bool:
    """Доступна ли опция стартового снаряжения по владениям."""
    return _option_available(option, weapon_proficiencies, armor_proficiencies)


def list_equipment_options_by_group(
    class_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Все опции выбора снаряжения по группам (без фильтра по владениям)."""
    result: dict[str, list[dict[str, Any]]] = {}
    for choice_group in list_equipment_choices(class_id):
        choice_id = str(choice_group.get("id", ""))
        if not choice_id:
            continue
        options = choice_group.get("options", [])
        if not isinstance(options, list):
            continue
        group = [dict(opt) for opt in options if isinstance(opt, dict)]
        if group:
            result[choice_id] = group
    return result


def option_needs_weapon_pick(option: dict[str, Any]) -> list[str]:
    """Пулы оружия, требующие выбора в опции."""
    pools: list[str] = []
    weapon_picks = option.get("weapon_picks", [])
    if isinstance(weapon_picks, list):
        for pick in weapon_picks:
            if isinstance(pick, dict) and pick.get("pool"):
                pools.append(str(pick["pool"]))
    return pools


def option_needs_tool_pick(option: dict[str, Any]) -> list[str]:
    """Пулы инструментов, требующие выбора в опции."""
    pools: list[str] = []
    tool_picks = option.get("tool_picks", [])
    if isinstance(tool_picks, list):
        for pick in tool_picks:
            if isinstance(pick, dict) and pick.get("pool"):
                pools.append(str(pick["pool"]))
    return pools


def option_armor_strength_requirement(option: dict[str, Any]) -> int | None:
    """Требование Силы для опции (максимум среди доспехов в items)."""
    max_req: int | None = None
    raw_items = option.get("items", [])
    if not isinstance(raw_items, list):
        return None
    for entry in raw_items:
        if not isinstance(entry, dict) or entry.get("kind") != "armor":
            continue
        armor_id = str(entry.get("id", ""))
        if armor_category(armor_id) == "shield":
            continue
        req = armor_strength_requirement(armor_id)
        if req is not None:
            max_req = req if max_req is None else max(max_req, req)
    return max_req
