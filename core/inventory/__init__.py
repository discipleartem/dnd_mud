"""Инвентарь персонажа, экипировка и расчёт КД."""

from core.inventory._ac import compute_ac
from core.inventory._equip import default_equipped, equip_defaults
from core.inventory._items import (
    ItemKind,
    add_items_to_inventory,
    expand_pack_contents,
    inventory_excluding_equipped,
    inventory_item_quantity,
    merge_inventory_items,
    normalize_inventory_item,
)
from core.inventory._names import item_display_name
from core.inventory._weapons import (
    dual_wielder_ac_bonus_applies,
    main_hand_uses_both_hands,
    weapon_is_two_handed,
    weapon_is_versatile,
)

__all__ = [
    "ItemKind",
    "add_items_to_inventory",
    "compute_ac",
    "default_equipped",
    "dual_wielder_ac_bonus_applies",
    "equip_defaults",
    "expand_pack_contents",
    "inventory_excluding_equipped",
    "inventory_item_quantity",
    "item_display_name",
    "main_hand_uses_both_hands",
    "merge_inventory_items",
    "normalize_inventory_item",
    "weapon_is_two_handed",
    "weapon_is_versatile",
]
