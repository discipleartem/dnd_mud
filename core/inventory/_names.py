"""Локализованные имена предметов (без UI-строк)."""

from core.equipment import (
    get_armor_name,
    get_equipment_item_name,
    get_tool_name,
    get_weapon_name,
)


def item_display_name(
    kind: str,
    item_id: str,
    language: str = "ru",
) -> str:
    """Имя предмета инвентаря на выбранном языке."""
    if kind == "weapon":
        return get_weapon_name(item_id, language)
    if kind == "armor":
        return get_armor_name(item_id, language)
    if kind == "tool":
        return get_tool_name(item_id, language)
    return get_equipment_item_name(item_id, language)
