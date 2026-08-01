"""Подписи и сводки стартового снаряжения класса (без resolve)."""

from typing import Any

from core.catalogs.equipment import (
    armor_category,
    load_equipment_item,
    proficiency_token_label,
)
from core.inventory.equipment_text import format_item_list_hint
from core.inventory.items import (
    expand_pack_contents,
    item_display_name,
)
from core.inventory.starting_equipment import (
    list_equipment_choices,
    list_fixed_items,
    option_armor_strength_requirement,
)
from core.platform.localization import get_string, resolve_localized_text
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


def equipment_choice_label(choice_id: str, strings: StringsDict) -> str:
    """Локализованная подпись группы выбора стартового снаряжения."""
    label = get_string(strings, f"equipment_choice.{choice_id}", default="")
    return label or choice_id


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


def _strip_proficiency_label_suffix(text: str) -> str:
    """Убрать «(если владеете)» из подписи опции."""
    for suffix in _PROFICIENCY_LABEL_SUFFIXES:
        if text.endswith(suffix):
            return text[: -len(suffix)]
    return text


def _option_pack_content_hints(
    option: dict[str, Any],
    language: str,
) -> list[str]:
    """Состав набора (pack), если опция — набор снаряжения."""
    raw_items = option.get("items", [])
    if not isinstance(raw_items, list):
        return []
    hints: list[str] = []
    for entry in raw_items:
        if not isinstance(entry, dict) or entry.get("kind") != "equipment":
            continue
        item_id = str(entry.get("id", ""))
        if load_equipment_item(item_id).get("category") != "pack":
            continue
        for content in expand_pack_contents(item_id):
            name = item_display_name(
                str(content["kind"]), str(content["id"]), language
            )
            qty = int(content.get("qty", 1))
            hints.append(f"{name} ×{qty}" if qty > 1 else name)
    return hints


def _option_mechanical_hints(
    option: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> list[str]:
    """КД доспехов и кубы урона оружия из items опции."""
    raw_items = option.get("items", [])
    if not isinstance(raw_items, list):
        return []
    hints: list[str] = []
    for entry in raw_items:
        if not isinstance(entry, dict):
            continue
        kind = str(entry.get("kind", ""))
        item_id = str(entry.get("id", ""))
        if kind not in ("armor", "weapon"):
            continue
        hint = format_item_list_hint(kind, item_id, strings, language)
        if hint:
            hints.append(hint)
    return hints


def format_equipment_option_label(
    option: dict[str, Any],
    strings: StringsDict,
    language: str,
) -> str:
    """Подпись опции без «(если владеете)»; тип / КД / кубы / состав набора."""
    label = option.get("label", {})
    if isinstance(label, dict):
        text = resolve_localized_text(label, language, fallback="?")
    else:
        text = str(label)
    text = _strip_proficiency_label_suffix(text)
    parts: list[str] = []
    req_key = equipment_option_requirement_key(option)
    if req_key:
        parts.append(proficiency_token_label(req_key, strings, language))
    pack_hints = _option_pack_content_hints(option, language)
    if pack_hints:
        parts.extend(pack_hints)
    else:
        parts.extend(_option_mechanical_hints(option, strings, language))
    if parts:
        text = f"{text} ({', '.join(parts)})"
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
