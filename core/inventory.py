"""Инвентарь, экипировка и КД — фасад публичного API."""

from core.armor_class import compute_ac, dual_wielder_ac_bonus_applies
from core.equip_defaults import (
    default_equipped,
    equip_defaults,
    main_hand_uses_both_hands,
    weapon_is_two_handed,
    weapon_is_versatile,
)
from core.inventory_items import (
    ItemKind,
    add_items_to_inventory,
    expand_pack_contents,
    inventory_excluding_equipped,
    inventory_item_quantity,
    item_display_name,
    merge_inventory_items,
    normalize_inventory_item,
)

__all__ = [
    "ItemKind",
    "normalize_inventory_item",
    "expand_pack_contents",
    "merge_inventory_items",
    "add_items_to_inventory",
    "inventory_item_quantity",
    "inventory_excluding_equipped",
    "item_display_name",
    "weapon_is_two_handed",
    "weapon_is_versatile",
    "main_hand_uses_both_hands",
    "dual_wielder_ac_bonus_applies",
    "compute_ac",
    "default_equipped",
    "equip_defaults",
]
