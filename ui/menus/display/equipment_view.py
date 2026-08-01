"""Инвентарь и экипировка на карточке."""

from colorama import Fore, Style

from core.catalogs.equipment import format_item_list_hint
from core.character.models import Character
from core.inventory.armor_class import compute_ac
from core.inventory.equipped_display import get_equipped_display
from core.inventory.items import (
    inventory_excluding_equipped,
    item_display_name,
)
from core.platform.localization import get_string, load_strings
from core.types import EquippedState, InventoryItem, StringsDict
from ui.menus.display.shared import _print_labeled_field


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


def format_inventory_line(
    inventory: list[InventoryItem],
    language: str = "ru",
    *,
    equipped: EquippedState | None = None,
) -> str:
    """Сжатый список инвентаря для UI (без экипированных предметов)."""
    strings = load_strings(language)
    display_items = inventory_excluding_equipped(inventory, equipped)
    parts: list[str] = []
    for item in display_items:
        kind = str(item.get("kind", ""))
        item_id = str(item.get("id", ""))
        qty = int(item.get("qty", 1))
        name = item_display_name(kind, item_id, language)
        hint = format_item_list_hint(kind, item_id, strings, language)
        if hint:
            name = f"{name} ({hint})"
        if qty > 1:
            parts.append(f"{name} ×{qty}")
        else:
            parts.append(name)
    return ", ".join(parts)
