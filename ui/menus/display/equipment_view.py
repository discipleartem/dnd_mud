"""Инвентарь и экипировка на карточке."""

from typing import Literal

from colorama import Fore, Style

from core.catalogs.equipment import (
    armor_equipped_hint,
    default_ammunition_pack_size,
    format_dice_for_display,
    get_armor_name,
    get_equipment_item_name,
    weapon_ammunition_item_id,
    weapon_damage_dice,
    weapon_property_hint,
    weapon_range,
    weapon_versatile_dice,
)
from core.character.models import Character
from core.inventory.armor_class import compute_ac
from core.inventory.equip_defaults import (
    default_equipped,
    main_hand_uses_both_hands,
    weapon_is_two_handed,
    weapon_is_versatile,
)
from core.inventory.items import (
    inventory_excluding_equipped,
    inventory_item_quantity,
    item_display_name,
)
from core.platform.localization import (
    get_string,
    load_strings,
)
from core.types import (
    EquippedState,
    InventoryItem,
    StringsDict,
)

# ============================================================================
# Общие хелперы подписей
# ============================================================================
from ui.menus.display.shared import (
    _print_labeled_field,
)


def _print_character_equipment(
    char: Character,
    strings: StringsDict,
    language: str,
    *,
    indent: str = "     ",
) -> None:
    """Экипировка, КД и инвентарь на карточке персонажа."""
    if char.equipped or char.inventory:
        ac = compute_ac(char)
        ac_display = f"{Fore.GREEN}{ac}{Style.RESET_ALL}"
        _print_labeled_field(
            strings,
            "choose_character.field_ac",
            ac_display,
            indent=indent,
        )
        equipped, off_hand_muted = get_equipped_display(char, language)
        header = get_string(strings, "choose_character.field_equipped")
        print(f"{indent}{Fore.LIGHTBLACK_EX}{header}{Style.RESET_ALL}")
        sub_indent = f"{indent}  "
        empty = get_string(strings, "choose_character.field_equipped_empty")
        slot_order = (
            ("armor", "choose_character.field_equipped_armor"),
            ("main_hand", "choose_character.field_equipped_main"),
            ("damage", "choose_character.field_equipped_damage"),
            ("off_hand", "choose_character.field_equipped_off"),
            ("ammunition", "choose_character.field_equipped_ammunition"),
            ("distance", "choose_character.field_equipped_range"),
        )
        hint_keys = {
            "armor": "armor_hint",
            "main_hand": "main_hand_hint",
            "off_hand": "off_hand_hint",
        }
        for key, label_key in slot_order:
            if key == "damage":
                if "damage_one_dice" not in equipped:
                    continue
            elif key not in equipped:
                continue
            cat_label = get_string(strings, label_key)
            if key == "damage":
                one = equipped["damage_one_dice"]
                two = equipped["damage_two_dice"]
                active = equipped["damage_active"]
                sep = f"{Fore.LIGHTBLACK_EX} | {Style.RESET_ALL}"
                if active == "one":
                    dice_line = (
                        f"{Fore.CYAN}{one}{Style.RESET_ALL}{sep}"
                        f"{Fore.LIGHTBLACK_EX}{two}{Style.RESET_ALL}"
                    )
                else:
                    dice_line = (
                        f"{Fore.LIGHTBLACK_EX}{one}{Style.RESET_ALL}{sep}"
                        f"{Fore.CYAN}{two}{Style.RESET_ALL}"
                    )
                print(
                    f"{sub_indent}{Fore.LIGHTBLACK_EX}"
                    f"{cat_label}{Style.RESET_ALL} {dice_line}"
                )
                continue
            value = equipped.get(key, empty)
            hint = equipped.get(hint_keys.get(key, ""), "")
            muted_off = key == "off_hand" and off_hand_muted
            if value == empty or muted_off:
                value_color = Fore.LIGHTBLACK_EX
            else:
                value_color = Fore.CYAN
            print(
                f"{sub_indent}{Fore.LIGHTBLACK_EX}"
                f"{cat_label}{Style.RESET_ALL} "
                f"{value_color}{value}{Style.RESET_ALL}",
                end="",
            )
            if hint and key in hint_keys:
                print(f" {Fore.LIGHTBLACK_EX}({hint})" f"{Style.RESET_ALL}")
            else:
                print()
    if char.inventory:
        inv_line = format_inventory_line(
            char.inventory, language, equipped=char.equipped
        )
        if inv_line:
            inv_display = f"{Fore.CYAN}{inv_line}{Style.RESET_ALL}"
            _print_labeled_field(
                strings,
                "choose_character.field_inventory",
                inv_display,
                indent=indent,
            )


# ============================================================================
# Отображение инвентаря и экипировки
# ============================================================================


def format_inventory_line(
    inventory: list[InventoryItem],
    language: str = "ru",
    *,
    equipped: EquippedState | None = None,
) -> str:
    """Сжатый список инвентаря для UI (без экипированных предметов)."""
    display_items = inventory_excluding_equipped(inventory, equipped)
    parts: list[str] = []
    for item in display_items:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        name = item_display_name(kind, item_id, language)
        if qty > 1:
            parts.append(f"{name} ×{qty}")
        else:
            parts.append(name)
    return ", ".join(parts)


def _versatile_active_grip(
    equipped: EquippedState,
) -> Literal["one_handed", "two_handed"]:
    """Текущий режим универсального оружия."""
    grip = equipped.get("main_hand_grip")
    if grip == "one_handed":
        return "one_handed"
    if grip == "two_handed":
        return "two_handed"
    if main_hand_uses_both_hands(equipped):
        return "two_handed"
    return "one_handed"


def _versatile_grip_hint(
    weapon_id: str,
    equipped: EquippedState,
    strings: StringsDict,
) -> str:
    """Подсказка хвата универсального оружия (одна / две руки)."""
    if not weapon_is_versatile(weapon_id):
        return ""
    if _versatile_active_grip(equipped) == "two_handed":
        key = "choose_character.field_equipped_versatile_grip_two"
    else:
        key = "choose_character.field_equipped_versatile_grip_one"
    return get_string(strings, key)


def format_versatile_damage_dice(
    weapon_id: str,
    equipped: EquippedState,
    language: str = "ru",
) -> tuple[str, str, str] | None:
    """Кости универсального оружия и активный режим: (1к8, 1к10, one|two)."""
    if not weapon_is_versatile(weapon_id):
        return None
    one_dice = format_dice_for_display(weapon_damage_dice(weapon_id), language)
    two_dice = format_dice_for_display(
        weapon_versatile_dice(weapon_id), language
    )
    active = (
        "two" if _versatile_active_grip(equipped) == "two_handed" else "one"
    )
    return one_dice, two_dice, active


def _loaded_ammunition_qty(
    inventory: list[InventoryItem], ammo_item_id: str
) -> int:
    """Боеприпасы «под рукой»: из инвентаря, до ёмкости колчана/сумки."""
    in_inv = inventory_item_quantity(inventory, "equipment", ammo_item_id)
    pack = default_ammunition_pack_size(ammo_item_id)
    return min(in_inv, pack) if in_inv > 0 else 0


def _equipped_weapon_for_range(equipped: EquippedState) -> str | None:
    """Оружие для строки дистанции (основная рука, затем вторая)."""
    for slot in ("main_hand", "off_hand"):
        weapon_id = equipped.get(slot)
        if isinstance(weapon_id, str) and weapon_range(weapon_id):
            return weapon_id
    return None


def get_equipped_display(
    character: Character,
    language: str = "ru",
) -> tuple[dict[str, str], bool]:
    """Локализованные подписи экипировки; bool — серая подпись второй руки."""
    strings = load_strings(language)
    empty = get_string(strings, "choose_character.field_equipped_empty")
    equipped = character.equipped or default_equipped()
    result: dict[str, str] = {}
    off_hand_muted = False
    armor_id = equipped.get("armor")
    if isinstance(armor_id, str) and armor_id:
        result["armor"] = item_display_name("armor", armor_id, language)
        armor_hint = armor_equipped_hint(armor_id, strings, language)
        if armor_hint:
            result["armor_hint"] = armor_hint
    else:
        result["armor"] = empty
    main_hand = equipped.get("main_hand")
    if isinstance(main_hand, str) and main_hand:
        result["main_hand"] = item_display_name("weapon", main_hand, language)
        hint_parts: list[str] = []
        prop_hint = weapon_property_hint(main_hand, strings, language)
        if prop_hint:
            hint_parts.append(prop_hint)
        grip_hint = _versatile_grip_hint(main_hand, equipped, strings)
        if grip_hint:
            hint_parts.append(grip_hint)
        if hint_parts:
            result["main_hand_hint"] = ", ".join(hint_parts)
        damage_dice = format_versatile_damage_dice(
            main_hand, equipped, language
        )
        if damage_dice:
            one, two, active = damage_dice
            result["damage_one_dice"] = one
            result["damage_two_dice"] = two
            result["damage_active"] = active
    else:
        result["main_hand"] = empty
    if main_hand_uses_both_hands(equipped) and isinstance(main_hand, str):
        if weapon_is_two_handed(main_hand):
            label_key = "choose_character.field_equipped_off_two_handed"
        else:
            label_key = "choose_character.field_equipped_off_versatile"
        result["off_hand"] = get_string(strings, label_key)
        off_hand_muted = True
    elif equipped.get("shield"):
        result["off_hand"] = get_armor_name("shield", language)
    else:
        off_hand = equipped.get("off_hand")
        if isinstance(off_hand, str) and off_hand:
            result["off_hand"] = item_display_name(
                "weapon", off_hand, language
            )
            hint = weapon_property_hint(off_hand, strings, language)
            if hint:
                result["off_hand_hint"] = hint
        else:
            result["off_hand"] = empty
    ammo_weapon = main_hand if isinstance(main_hand, str) else None
    if ammo_weapon:
        ammo_id = weapon_ammunition_item_id(ammo_weapon)
        if ammo_id:
            qty = _loaded_ammunition_qty(character.inventory, ammo_id)
            result["ammunition"] = get_string(
                strings,
                "choose_character.field_equipped_ammunition_value",
                type=get_equipment_item_name(ammo_id, language),
                qty=qty,
            )
    range_weapon = _equipped_weapon_for_range(equipped)
    if range_weapon:
        rng = weapon_range(range_weapon)
        if rng:
            result["distance"] = get_string(
                strings,
                "choose_character.field_equipped_range_value",
                normal=rng["normal"],
                long=rng["long"],
            )
    return result, off_hand_muted


# ============================================================================
# Отображение классов и подклассов
# ============================================================================
