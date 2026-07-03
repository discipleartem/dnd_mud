"""Секции карточки персонажа: владения, навыки, экипировка."""

from colorama import Fore, Style

from core.equipment import proficiency_token_label
from core.inventory import compute_ac
from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus._common import _ability_name, _skill_name
from ui.menus._display._character_header import (
    _empty_field_value,
    _print_labeled_field,
)
from ui.menus._display._inventory import (
    format_inventory_line,
    get_equipped_display,
)
from ui.menus.expertise import format_expertise_display


def _format_proficiency_token_list(
    strings: StringsDict,
    tokens: list[str],
    *,
    language: str = "ru",
) -> str:
    """Локализованный список токенов владений."""
    names = [proficiency_token_label(t, strings, language) for t in tokens]
    return ", ".join(names)


def _print_character_proficiencies(
    char: Character,
    strings: StringsDict,
    language: str,
    *,
    indent: str = "     ",
) -> None:
    """Владения персонажа: заголовок и категории с отступом."""
    categories: tuple[tuple[list[str], str], ...] = (
        (
            char.armor_proficiencies,
            "choose_character.field_proficiencies_armor",
        ),
        (
            char.weapon_proficiencies,
            "choose_character.field_proficiencies_weapons",
        ),
        (
            char.tool_proficiencies,
            "choose_character.field_proficiencies_tools",
        ),
    )
    has_any = any(tokens for tokens, _ in categories)
    if not has_any:
        _print_labeled_field(
            strings,
            "choose_character.field_proficiencies",
            _empty_field_value(strings),
            indent=indent,
        )
        return

    header = get_string(strings, "choose_character.field_proficiencies")
    print(f"{indent}{Fore.LIGHTBLACK_EX}{header}{Style.RESET_ALL}")
    sub_indent = f"{indent}  "
    for tokens, label_key in categories:
        if not tokens:
            continue
        value = _format_proficiency_token_list(
            strings,
            tokens,
            language=language,
        )
        cat_label = get_string(strings, label_key)
        print(
            f"{sub_indent}{Fore.LIGHTBLACK_EX}{cat_label}{Style.RESET_ALL} "
            f"{Fore.CYAN}{value}{Style.RESET_ALL}"
        )


def _print_character_skills_and_expertise(
    char: Character,
    strings: StringsDict,
    *,
    indent: str = "     ",
) -> None:
    """Навыки и компетентность на карточке персонажа."""
    if char.skills:
        skills_line = ", ".join(
            _skill_name(strings, skill_id) for skill_id in char.skills
        )
        skills_display = f"{Fore.CYAN}{skills_line}{Style.RESET_ALL}"
    else:
        skills_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_skills",
        skills_display,
        indent=indent,
    )

    expertise_line = format_expertise_display(
        strings, char.skill_expertise, char.tool_expertise
    )
    expertise_display = (
        f"{Fore.CYAN}{expertise_line}{Style.RESET_ALL}"
        if expertise_line
        else _empty_field_value(strings)
    )
    _print_labeled_field(
        strings,
        "choose_character.field_expertise",
        expertise_display,
        indent=indent,
    )


def _print_character_saving_throws(
    char: Character,
    strings: StringsDict,
    *,
    indent: str = "     ",
) -> None:
    """Спасброски на карточке персонажа."""
    if not char.save_proficiencies:
        return
    parts: list[str] = []
    for ability_id in char.save_proficiencies:
        name = _ability_name(strings, ability_id)
        parts.append(name)
    value = f"{Fore.CYAN}{', '.join(parts)}{Style.RESET_ALL}"
    _print_labeled_field(
        strings,
        "choose_character.field_saving_throws",
        value,
        indent=indent,
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
