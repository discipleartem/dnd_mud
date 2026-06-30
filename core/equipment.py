"""Загрузка каталога снаряжения из YAML."""

from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog
from core.localization import get_string, resolve_localized_text
from core.types import StringsDict

WEAPONS_FILE = Path("database/equipment/weapon.yaml")
ARMOR_FILE = Path("database/equipment/armor.yaml")
TOOLS_FILE = Path("database/equipment/tools.yaml")
EQUIPMENT_FILE = Path("database/equipment/equipment.yaml")

# Пулы инструментов для proficiencies
TOOL_POOL_CATEGORIES: dict[str, str] = {
    "artisans_tools": "artisans_tools",
    "gaming_sets": "gaming_sets",
    "musical_instruments": "musical_instruments",
    "land_vehicles": "land_vehicles",
    "water_vehicles": "water_vehicles",
}

SIMPLE_CATEGORIES = frozenset({"simple_melee", "simple_ranged"})
MARTIAL_CATEGORIES = frozenset({"martial_melee", "martial_ranged"})


def _item_name(name: Any, language: str, fallback: str) -> str:
    """Имя предмета: строка или {ru, en}."""
    if isinstance(name, dict):
        return resolve_localized_text(name, language, fallback=fallback)
    if isinstance(name, str):
        return name
    return fallback


def _load_weapons() -> dict[str, Any]:
    return load_catalog(WEAPONS_FILE, "weapons")


def _load_armor() -> dict[str, Any]:
    return load_catalog(ARMOR_FILE, "armor")


def _load_tools() -> dict[str, Any]:
    return load_catalog(TOOLS_FILE, "tools")


def _load_equipment_items() -> dict[str, Any]:
    return load_catalog(EQUIPMENT_FILE, "equipment")


def all_weapon_ids() -> list[str]:
    """ID всего оружия из каталога."""
    return sorted(_load_weapons().keys())


def all_tool_ids() -> list[str]:
    """ID всех инструментов из каталога."""
    return sorted(_load_tools().keys())


def load_weapon(weapon_id: str) -> dict[str, Any]:
    """Данные оружия по id."""
    info = _load_weapons().get(weapon_id, {})
    return dict(info) if isinstance(info, dict) else {}


def load_armor(armor_id: str) -> dict[str, Any]:
    """Данные доспеха по id."""
    info = _load_armor().get(armor_id, {})
    return dict(info) if isinstance(info, dict) else {}


def load_tool(tool_id: str) -> dict[str, Any]:
    """Данные инструмента по id."""
    info = _load_tools().get(tool_id, {})
    return dict(info) if isinstance(info, dict) else {}


def load_equipment_item(item_id: str) -> dict[str, Any]:
    """Данные предмета снаряжения по id."""
    info = _load_equipment_items().get(item_id, {})
    return dict(info) if isinstance(info, dict) else {}


def weapon_category(weapon_id: str) -> str:
    """Категория оружия (simple_melee, martial_ranged, …)."""
    return str(load_weapon(weapon_id).get("category", ""))


def armor_category(armor_id: str) -> str:
    """Категория доспеха (light, medium, heavy) или shield."""
    cat = load_armor(armor_id).get("category", "")
    return str(cat)


def tool_category(tool_id: str) -> str:
    """Категория инструмента."""
    return str(load_tool(tool_id).get("category", ""))


def tools_by_category(category: str) -> list[str]:
    """Id инструментов в категории или пуле."""
    if category in TOOL_POOL_CATEGORIES:
        category = TOOL_POOL_CATEGORIES[category]
    result: list[str] = []
    for tool_id, info in _load_tools().items():
        if isinstance(info, dict) and info.get("category") == category:
            result.append(str(tool_id))
    return result


def resolve_tool_pool(pool: str) -> list[str]:
    """Разрешить pool-токен в список tool id."""
    if pool in _load_tools():
        return [pool]
    return tools_by_category(pool)


def get_weapon_name(weapon_id: str, language: str = "ru") -> str:
    """Локализованное имя оружия."""
    info = load_weapon(weapon_id)
    return _item_name(info.get("name", weapon_id), language, weapon_id)


def get_armor_name(armor_id: str, language: str = "ru") -> str:
    """Локализованное имя доспеха."""
    info = load_armor(armor_id)
    return _item_name(info.get("name", armor_id), language, armor_id)


def get_tool_name(tool_id: str, language: str = "ru") -> str:
    """Локализованное имя инструмента."""
    info = load_tool(tool_id)
    return _item_name(info.get("name", tool_id), language, tool_id)


def proficiency_token_label(
    token: str,
    strings: StringsDict,
    language: str = "ru",
) -> str:
    """Локализованная подпись токена владения."""
    localized = get_string(strings, f"proficiency.{token}", default="")
    if localized:
        return localized
    tool_label = get_string(strings, f"tools.{token}", default="")
    if tool_label:
        return tool_label
    if weapon_category(token):
        return get_weapon_name(token, language)
    if armor_category(token) or token in _load_armor():
        return get_armor_name(token, language)
    if token in _load_tools():
        return get_tool_name(token, language)
    return token


def weapon_matches_category(category: str, weapon_id: str) -> bool:
    """Оружие входит в категорию proficiencies."""
    wc = weapon_category(weapon_id)
    if not wc:
        return False
    if category == "simple":
        return wc in SIMPLE_CATEGORIES
    if category == "martial":
        return wc in MARTIAL_CATEGORIES
    if category == "simple_melee":
        return wc == "simple_melee"
    if category == "simple_ranged":
        return wc == "simple_ranged"
    if category == "martial_melee":
        return wc == "martial_melee"
    if category == "martial_ranged":
        return wc == "martial_ranged"
    return category == wc
