"""Текстовые подсказки для UI по снаряжению (кости, свойства, доспехи)."""

from core.catalogs.equipment import (
    armor_category,
    load_armor,
    weapon_damage_dice,
    weapon_properties_raw,
    weapon_versatile_dice,
)
from core.platform.localization import get_string
from core.types import StringsDict

_HINT_SKIP_PROPERTIES = frozenset({"ammunition", "thrown", "versatile"})

_WEAPON_PROPERTY_ORDER = (
    "ammunition",
    "two_handed",
    "reach",
    "heavy",
    "loading",
    "light",
    "finesse",
    "thrown",
    "versatile",
    "special",
)


def format_dice_for_display(dice: str, language: str) -> str:
    """Кости в подписи: 1d10 → 1к10 для ru."""
    if language == "ru":
        return dice.replace("d", "к")
    return dice


def format_weapon_property_labels(
    weapon_id: str,
    strings: StringsDict,
    language: str = "ru",
) -> list[str]:
    """Короткие подписи свойств оружия для UI (как в PHB, табл. снаряжения)."""
    props = weapon_properties_raw(weapon_id)
    if not props:
        return []
    labels: list[str] = []
    for key in _WEAPON_PROPERTY_ORDER:
        if key in _HINT_SKIP_PROPERTIES:
            continue
        if key not in props:
            continue
        value = props[key]
        if value is True or value:
            labels.append(get_string(strings, f"weapon_property.{key}"))
    return labels


def format_versatile_catalog_hint(
    weapon_id: str,
    strings: StringsDict,
    language: str = "ru",
) -> str | None:
    """Подсказка для меню: оба режима без указания активного."""
    if "versatile" not in weapon_properties_raw(weapon_id):
        return None
    one_dice = format_dice_for_display(weapon_damage_dice(weapon_id), language)
    two_dice = format_dice_for_display(
        weapon_versatile_dice(weapon_id), language
    )
    return get_string(
        strings,
        "weapon_property.versatile_catalog",
        one_dice=one_dice,
        two_dice=two_dice,
    )


def weapon_property_hint(
    weapon_id: str, strings: StringsDict, language: str = "ru"
) -> str:
    """Свойства оружия одной строкой для подсказки в UI."""
    return ", ".join(
        format_weapon_property_labels(weapon_id, strings, language)
    )


def armor_equipped_hint(
    armor_id: str, strings: StringsDict, language: str = "ru"
) -> str:
    """Подсказка к экипированному доспеху по таблице PHB."""
    cat = armor_category(armor_id)
    if cat not in ("light", "medium", "heavy"):
        return ""
    info = load_armor(armor_id)
    ac = int(info.get("armor_class", 10))
    category = get_string(strings, f"armor_category.{cat}")
    base = get_string(
        strings,
        f"armor_equipped_hint.{cat}",
        category=category,
        ac=ac,
    )
    parts = [base]
    str_req = info.get("strength_requirement")
    if isinstance(str_req, int) and str_req > 0:
        parts.append(
            get_string(strings, "armor_equipped_hint.strength", value=str_req)
        )
    if info.get("stealth_disadvantage"):
        parts.append(get_string(strings, "armor_equipped_hint.stealth"))
    return ", ".join(parts)
