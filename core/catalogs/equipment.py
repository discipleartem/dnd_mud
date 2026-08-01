"""Загрузка каталога снаряжения из YAML."""

from pathlib import Path
from typing import Any

from core.platform.catalog_loader import load_catalog
from core.platform.localization import (
    get_string,
    load_strings,
    resolve_localized_text,
)
from core.types import LanguageCode, StringsDict

WEAPONS_FILE = Path("database/equipment/weapon.yaml")
ARMOR_FILE = Path("database/equipment/armor.yaml")
TOOLS_FILE = Path("database/equipment/tools.yaml")
EQUIPMENT_FILE = Path("database/equipment/equipment.yaml")

CUSTOM_TOOL_POOLS: dict[str, list[str]] = {
    "soldier_gaming": ["dice_set", "playing_cards"],
}

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


def _load_catalog_item(
    catalog: dict[str, Any], item_id: str
) -> dict[str, Any]:
    """Один элемент из загруженного каталога."""
    info = catalog.get(item_id, {})
    return dict(info) if isinstance(info, dict) else {}


def all_weapon_ids() -> list[str]:
    """ID всего оружия из каталога."""
    return sorted(_load_weapons().keys())


def all_tool_ids() -> list[str]:
    """ID всех инструментов из каталога."""
    return sorted(_load_tools().keys())


def load_weapon(weapon_id: str) -> dict[str, Any]:
    """Данные оружия по id."""
    return _load_catalog_item(_load_weapons(), weapon_id)


def load_armor(armor_id: str) -> dict[str, Any]:
    """Данные доспеха по id."""
    return _load_catalog_item(_load_armor(), armor_id)


def load_tool(tool_id: str) -> dict[str, Any]:
    """Данные инструмента по id."""
    return _load_catalog_item(_load_tools(), tool_id)


def load_equipment_item(item_id: str) -> dict[str, Any]:
    """Данные предмета снаряжения по id."""
    return _load_catalog_item(_load_equipment_items(), item_id)


def weapon_category(weapon_id: str) -> str:
    """Категория оружия (simple_melee, martial_ranged, …)."""
    return str(load_weapon(weapon_id).get("category", ""))


def armor_category(armor_id: str) -> str:
    """Категория доспеха (light, medium, heavy) или shield."""
    cat = load_armor(armor_id).get("category", "")
    return str(cat)


def armor_strength_requirement(armor_id: str) -> int | None:
    """Минимальная Сила для доспеха (PHB) или None."""
    req = load_armor(armor_id).get("strength_requirement")
    if isinstance(req, int) and req > 0:
        return req
    return None


def meets_armor_strength_requirement(armor_id: str, strength: int) -> bool:
    """Достаточна ли Сила для ношения доспеха."""
    req = armor_strength_requirement(armor_id)
    if req is None:
        return True
    return strength >= req


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
    custom = CUSTOM_TOOL_POOLS.get(pool)
    if custom is not None:
        return list(custom)
    if pool in _load_tools():
        return [pool]
    return tools_by_category(pool)


def get_weapon_name(weapon_id: str, language: str = "ru") -> str:
    """Локализованное имя оружия; для двуручного ближнего — префикс."""
    info = load_weapon(weapon_id)
    name = _item_name(info.get("name", weapon_id), language, weapon_id)
    props = info.get("properties")
    if not isinstance(props, dict) or not props.get("two_handed"):
        return name
    category = str(info.get("category", ""))
    if not category.endswith("_melee"):
        return name
    lower = name.casefold()
    if "двуручн" in lower or "two-handed" in lower:
        return name
    lang: LanguageCode = "en" if language == "en" else "ru"
    prefix = get_string(
        load_strings(lang),
        "weapon_name.two_handed_prefix",
        default="",
    )
    if not prefix:
        return name
    return f"{prefix}{name}"


_WEAPON_AMMUNITION_ITEM: dict[str, str] = {
    "light_crossbow": "crossbow_bolts",
    "heavy_crossbow": "crossbow_bolts",
    "hand_crossbow": "crossbow_bolts",
    "shortbow": "arrows",
    "longbow": "arrows",
    "sling": "sling_bullets",
    "blowgun": "blowgun_needles",
}


def weapon_properties_raw(weapon_id: str) -> dict[str, Any]:
    """Свойства оружия из YAML (light, versatile, …)."""
    props = load_weapon(weapon_id).get("properties")
    return dict(props) if isinstance(props, dict) else {}


def weapon_damage_dice(weapon_id: str) -> str:
    damage = load_weapon(weapon_id).get("damage", {})
    if isinstance(damage, dict):
        return str(damage.get("dice", "1d4"))
    return "1d4"


def weapon_versatile_dice(weapon_id: str) -> str:
    props = weapon_properties_raw(weapon_id).get("versatile")
    if props:
        return str(props)
    return weapon_damage_dice(weapon_id)


def weapon_ammunition_item_id(weapon_id: str) -> str | None:
    """ID боеприпаса для оружия с свойством «боеприпас»."""
    if "ammunition" not in weapon_properties_raw(weapon_id):
        return None
    return _WEAPON_AMMUNITION_ITEM.get(weapon_id)


def weapon_range(weapon_id: str) -> dict[str, int] | None:
    """Дистанция оружия: normal/long из боеприпаса или метательного."""
    props = weapon_properties_raw(weapon_id)
    for key in ("ammunition", "thrown"):
        raw = props.get(key)
        if isinstance(raw, dict) and "normal" in raw and "long" in raw:
            return {"normal": int(raw["normal"]), "long": int(raw["long"])}
    return None


def default_ammunition_pack_size(ammo_item_id: str) -> int:
    """Ёмкость колчана/сумки по умолчанию (из quantity в YAML)."""
    info = load_equipment_item(ammo_item_id)
    qty = info.get("quantity")
    if isinstance(qty, int) and qty > 0:
        return qty
    return 20


def get_armor_name(armor_id: str, language: str = "ru") -> str:
    """Локализованное имя доспеха."""
    info = load_armor(armor_id)
    return _item_name(info.get("name", armor_id), language, armor_id)


def get_tool_name(tool_id: str, language: str = "ru") -> str:
    """Локализованное имя инструмента."""
    info = load_tool(tool_id)
    return _item_name(info.get("name", tool_id), language, tool_id)


def get_equipment_item_name(item_id: str, language: str = "ru") -> str:
    """Локализованное имя предмета снаряжения."""
    info = load_equipment_item(item_id)
    return _item_name(info.get("name", item_id), language, item_id)


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


from core.inventory.equipment_text import (  # noqa: E402
    armor_equipped_hint,
    format_armor_list_ac,
    format_dice_for_display,
    format_item_list_hint,
    format_versatile_catalog_hint,
    format_weapon_list_damage,
    format_weapon_property_labels,
    weapon_property_hint,
)

__all__ = [
    "armor_equipped_hint",
    "format_armor_list_ac",
    "format_dice_for_display",
    "format_item_list_hint",
    "format_versatile_catalog_hint",
    "format_weapon_list_damage",
    "format_weapon_property_labels",
    "weapon_property_hint",
]
