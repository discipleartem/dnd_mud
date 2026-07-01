"""Выбор стартового снаряжения класса при создании персонажа."""

from typing import Any

from colorama import Fore, Style

from core.equipment import get_tool_name, get_weapon_name
from core.localization import get_string
from core.proficiency_checks import (
    has_tool_proficiency,
    has_weapon_proficiency,
)
from core.starting_equipment import (
    all_weapons_in_pool,
    equipment_option_available,
    format_equipment_option_label,
    list_equipment_options_by_group,
    list_fixed_items,
    option_needs_tool_pick,
    option_needs_weapon_pick,
    tools_for_pool,
)
from core.types import StringsDict
from ui.menus._common import (
    _format_pick_menu_label,
    _print_screen_header,
    _read_numbered_choice,
    _run_numbered_menu,
    _sort_ids_by_proficiency,
)


def _pick_weapon_from_pool(
    strings: StringsDict,
    pool: str,
    weapon_proficiencies: list[str],
    language: str,
) -> str | None:
    """Выбор оружия из пула."""
    weapons = _sort_ids_by_proficiency(
        all_weapons_in_pool(pool),
        weapon_proficiencies,
        has_weapon_proficiency,
        name_key=lambda weapon_id: get_weapon_name(weapon_id, language),
    )
    if not weapons:
        return None
    labels = [
        _format_pick_menu_label(
            get_weapon_name(weapon_id, language),
            has_weapon_proficiency(weapon_proficiencies, weapon_id),
        )
        for weapon_id in weapons
    ]
    _print_screen_header(
        get_string(strings, "character.equipment_weapon_pick")
    )
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.equipment_weapon_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    return weapons[choice - 1]


def _pick_tool_from_pool(
    strings: StringsDict,
    pool: str,
    tool_proficiencies: list[str],
    language: str,
) -> str | None:
    """Выбор инструмента из пула."""
    tools = _sort_ids_by_proficiency(
        tools_for_pool(pool),
        tool_proficiencies,
        has_tool_proficiency,
        name_key=lambda tool_id: get_tool_name(tool_id, language),
    )
    if not tools:
        return None
    labels = [
        _format_pick_menu_label(
            get_tool_name(tool_id, language),
            has_tool_proficiency(tool_proficiencies, tool_id),
        )
        for tool_id in tools
    ]
    _print_screen_header(get_string(strings, "character.equipment_tool_pick"))
    choice = _run_numbered_menu(
        strings,
        labels,
        prompt_key="character.equipment_tool_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    return tools[choice - 1]


def _pick_option_for_group(
    strings: StringsDict,
    choice_id: str,
    options: list[dict[str, Any]],
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
    tool_proficiencies: list[str],
    language: str,
) -> dict[str, str] | None:
    """Выбор одной группы снаряжения; возвращает фрагмент equipment_choices."""
    selectable = [
        opt
        for opt in options
        if equipment_option_available(
            opt, weapon_proficiencies, armor_proficiencies
        )
    ]
    _print_screen_header(
        get_string(strings, "character.equipment_choice_heading", id=choice_id)
    )
    for opt in options:
        label = format_equipment_option_label(opt, strings, language)
        if equipment_option_available(
            opt, weapon_proficiencies, armor_proficiencies
        ):
            idx = selectable.index(opt) + 1
            print(
                f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
                f"{Fore.CYAN}{label}{Style.RESET_ALL}"
            )
        else:
            print(f"  {Fore.LIGHTBLACK_EX}{label}{Style.RESET_ALL}")
    choice = _read_numbered_choice(
        strings,
        len(selectable),
        prompt_key="character.equipment_option_prompt",
        back_label_key="character.back",
    )
    if choice is None:
        return None
    selected = selectable[choice - 1]
    option_id = str(selected.get("id", ""))
    result: dict[str, str] = {choice_id: option_id}
    for idx, pool in enumerate(option_needs_weapon_pick(selected)):
        weapon_id = _pick_weapon_from_pool(
            strings, pool, weapon_proficiencies, language
        )
        if weapon_id is None:
            return None
        result[f"{choice_id}_weapon_{idx}"] = weapon_id
    for idx, pool in enumerate(option_needs_tool_pick(selected)):
        tool_id = _pick_tool_from_pool(
            strings, pool, tool_proficiencies, language
        )
        if tool_id is None:
            return None
        result[f"{choice_id}_tool_{idx}"] = tool_id
    return result


def select_creation_equipment(
    strings: StringsDict,
    class_id: str,
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
    tool_proficiencies: list[str],
    language: str = "ru",
) -> dict[str, str] | None:
    """Шаг выбора стартового снаряжения класса."""
    option_groups = list_equipment_options_by_group(class_id)
    fixed = list_fixed_items(class_id)
    if not option_groups and not fixed:
        return {}

    _print_screen_header(get_string(strings, "character.equipment_caption"))
    if fixed:
        print(get_string(strings, "character.equipment_fixed_heading"))
        for item in fixed:
            kind = str(item.get("kind", ""))
            item_id = str(item.get("id", ""))
            qty = int(item.get("qty", 1))
            if kind == "weapon":
                name = get_weapon_name(item_id, language)
            elif kind == "armor":
                from core.equipment import get_armor_name

                name = get_armor_name(item_id, language)
            elif kind == "tool":
                name = get_tool_name(item_id, language)
            else:
                from core.equipment import get_equipment_item_name

                name = get_equipment_item_name(item_id, language)
            line = f"  {Fore.CYAN}• {name}{Style.RESET_ALL}"
            if qty > 1:
                line += f" {Fore.LIGHTBLACK_EX}×{qty}{Style.RESET_ALL}"
            print(line)
        print()

    choices: dict[str, str] = {}
    for choice_id, options in option_groups.items():
        picked = _pick_option_for_group(
            strings,
            choice_id,
            options,
            weapon_proficiencies,
            armor_proficiencies,
            tool_proficiencies,
            language,
        )
        if picked is None:
            return None
        choices.update(picked)
    return choices
