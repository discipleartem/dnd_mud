"""Стартовое снаряжение класса из YAML."""

from typing import Any

from core.classes import get_class_dict
from core.equipment import (
    all_weapon_ids,
    armor_category,
    armor_strength_requirement,
    resolve_tool_pool,
    weapon_matches_category,
)
from core.inventory import (
    add_items_to_inventory,
    item_display_name,
    normalize_inventory_item,
)
from core.localization import get_string, resolve_localized_text
from core.proficiency_checks import (
    has_weapon_pool_proficiency,
    has_weapon_proficiency,
)
from core.types import StringsDict

_PROFICIENCY_LABEL_SUFFIXES = (
    " (если владеете)",
    " (if proficient)",
)

CHOICE_ID_CATEGORY: dict[str, str] = {
    "weapon": "weapon",
    "armor": "armor",
    "ranged": "weapon",
    "melee": "weapon",
    "weapon_primary": "weapon",
    "ranged_or_axes": "weapon",
    "instrument": "tool",
    "pack": "gear",
    "focus": "gear",
}

FIXED_ITEM_CATEGORY: dict[str, str] = {
    "weapon": "weapon",
    "armor": "armor",
    "tool": "tool",
    "equipment": "gear",
}

STARTING_EQUIPMENT_SECTION_ORDER = ("weapon", "armor", "tool", "gear")

STARTING_EQUIPMENT_SECTION_KEYS: dict[str, str] = {
    "weapon": "character.class_starting_equipment_weapons",
    "armor": "character.class_starting_equipment_armor",
    "tool": "character.class_starting_equipment_tools",
    "gear": "character.class_starting_equipment_other",
}


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
    weapon_proficiencies: list[str],
) -> list[dict[str, Any]]:
    """Собрать предметы из выбранной опции."""
    items: list[dict[str, Any]] = []
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
) -> list[dict[str, Any]]:
    """Разрешить стартовое снаряжение класса в список предметов."""
    inventory: list[dict[str, Any]] = []
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
                weapon_proficiencies,
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


def filter_available_options(
    class_id: str,
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """Доступные опции по группам выбора."""
    result: dict[str, list[dict[str, Any]]] = {}
    for choice_group in list_equipment_choices(class_id):
        choice_id = str(choice_group.get("id", ""))
        if not choice_id:
            continue
        options = choice_group.get("options", [])
        if not isinstance(options, list):
            continue
        available = [
            dict(opt)
            for opt in options
            if isinstance(opt, dict)
            and _option_available(
                opt, weapon_proficiencies, armor_proficiencies
            )
        ]
        if available:
            result[choice_id] = available
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


def _strip_proficiency_label_suffix(text: str) -> str:
    """Убрать «(если владеете)» из подписи опции."""
    for suffix in _PROFICIENCY_LABEL_SUFFIXES:
        if text.endswith(suffix):
            return text[: -len(suffix)]
    return text


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


def equipment_option_strength_warning(
    option: dict[str, Any],
    strength: int,
    strings: StringsDict,
) -> str | None:
    """Подпись «Сил N», если персонаж не тянет доспех опции."""
    req = option_armor_strength_requirement(option)
    if req is None or strength >= req:
        return None
    return get_string(strings, "armor_equipped_hint.strength", value=req)


def equipment_option_requirement_key(option: dict[str, Any]) -> str | None:
    """Ключ владения для подсказки в скобках (light, martial, …)."""
    req_armor = option.get("requires_armor")
    if isinstance(req_armor, str):
        return req_armor
    req_weapon = option.get("requires_weapon_pool")
    if isinstance(req_weapon, str):
        return req_weapon
    raw_items = option.get("items", [])
    if isinstance(raw_items, list):
        for entry in raw_items:
            if not isinstance(entry, dict) or entry.get("kind") != "armor":
                continue
            cat = armor_category(str(entry.get("id", "")))
            if cat and cat != "shield":
                return cat
    return None


def format_equipment_option_label(
    option: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> str:
    """Подпись опции без «(если владеете)»; тип доспеха/оружия в скобках."""
    label = option.get("label", {})
    if isinstance(label, dict):
        text = resolve_localized_text(label, language, fallback="?")
    else:
        text = str(label)
    text = _strip_proficiency_label_suffix(text)
    req_key = equipment_option_requirement_key(option)
    if req_key:
        hint = get_string(strings, f"proficiency.{req_key}", default=req_key)
        text = f"{text} ({hint})"
    return text


def summarize_class_starting_equipment(
    class_id: str,
    strings: StringsDict,
    language: str,
) -> dict[str, list[str]]:
    """Стартовое снаряжение класса, сгруппированное по категориям."""
    sections: dict[str, list[str]] = {
        key: [] for key in STARTING_EQUIPMENT_SECTION_ORDER
    }
    for item in list_fixed_items(class_id):
        kind = str(item.get("kind", ""))
        category = FIXED_ITEM_CATEGORY.get(kind, "gear")
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        name = item_display_name(kind, item_id, language)
        if qty > 1:
            name = f"{name} ×{qty}"
        sections[category].append(name)
    for group in list_equipment_choices(class_id):
        choice_id = str(group.get("id", ""))
        category = CHOICE_ID_CATEGORY.get(choice_id, "gear")
        options = group.get("options", [])
        if not isinstance(options, list):
            continue
        for option in options:
            if isinstance(option, dict):
                sections[category].append(
                    format_equipment_option_label(option, strings, language)
                )
    return {key: lines for key, lines in sections.items() if lines}
