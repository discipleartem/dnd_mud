"""Выбор владений снаряжением при создании персонажа."""

from typing import Any

from colorama import Fore, Style

from core.catalogs.equipment import get_tool_name, proficiency_token_label
from core.feats.grant_merge import resolve_creation_grants_with_feats
from core.mechanics.proficiencies import (
    ProficiencyChoice,
    get_proficiency_choices,
    has_tool_proficiency,
    is_valid_tool_selection,
)
from core.platform.io import merge_unique
from core.platform.localization import get_string
from core.progression.class_progression import start_level_for_difficulty
from core.types import GameDifficulty, StringsDict
from ui.menus.console import (
    format_pick_menu_label,
    print_screen_header,
    read_pool_pick,
    sort_ids_by_proficiency,
)


def _format_list(
    strings: StringsDict, tokens: list[str], language: str
) -> str:
    """Список владений для отображения."""
    if not tokens:
        return get_string(strings, "character.proficiencies_none")
    return ", ".join(
        proficiency_token_label(t, strings, language) for t in tokens
    )


def _print_summary(
    strings: StringsDict,
    weapons: list[str],
    armors: list[str],
    tools: list[str],
    language: str,
) -> None:
    """Показать уже полученные владения."""
    print(
        f"{Fore.CYAN}{get_string(strings, 'character.proficiencies_heading')}"
        f"{Style.RESET_ALL}"
    )
    print()
    a_list = _format_list(strings, armors, language)
    w_list = _format_list(strings, weapons, language)
    t_list = _format_list(strings, tools, language)
    a_line = get_string(strings, "character.proficiencies_armor", list=a_list)
    w_line = get_string(
        strings, "character.proficiencies_weapons", list=w_list
    )
    t_line = get_string(strings, "character.proficiencies_tools", list=t_list)
    print(f"  {a_line}")
    print(f"  {w_line}")
    print(f"  {t_line}")
    print()


def _pick_tools(
    strings: StringsDict,
    choice: ProficiencyChoice,
    known_tools: list[str],
    language: str,
    pick_index: int,
    pick_total: int,
) -> list[str] | None:
    """Выбор инструментов из пула."""
    pool = list(choice.options or [])
    if not pool:
        return []
    added: list[str] = []
    current = list(known_tools)
    for pick_idx in range(1, choice.count + 1):
        while True:
            print_screen_header(
                get_string(strings, "character.proficiencies_caption")
            )
            source_label = get_string(
                strings, f"character.proficiencies_source_{choice.source}"
            )
            prompt = get_string(
                strings,
                "character.proficiencies_tool_pick_prompt",
                source=source_label,
                current=pick_index + pick_idx - 1,
                total=pick_total,
            )
            print(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
            print()
            taken_ids = [tool_id for tool_id in pool if tool_id in current]
            for tool_id in taken_ids:
                name = get_tool_name(tool_id, language)
                taken = get_string(
                    strings, "character.proficiencies_taken_suffix"
                )
                print(
                    f"  {Fore.LIGHTBLACK_EX}{name} {taken}"
                    f"{Style.RESET_ALL}"
                )
            selectable = sort_ids_by_proficiency(
                [tool_id for tool_id in pool if tool_id not in current],
                known_tools,
                has_tool_proficiency,
                name_key=lambda tool_id: get_tool_name(tool_id, language),
            )
            for idx, tool_id in enumerate(selectable, 1):
                name = get_tool_name(tool_id, language)
                label = format_pick_menu_label(
                    name,
                    has_tool_proficiency(known_tools, tool_id),
                )
                print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {label}")
            tool_prompt = get_string(
                strings, "character.proficiencies_tool_prompt"
            )
            picked_id = read_pool_pick(
                strings,
                selectable,
                prompt=tool_prompt,
                empty_key="character.expertise_pool_empty",
            )
            if picked_id == "":
                continue
            if picked_id is None:
                return None
            added.append(picked_id)
            current.append(picked_id)
            break
    return added


def select_creation_proficiencies(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    difficulty: GameDifficulty,
    language: str = "ru",
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]] | None:
    """Выбор владений; None — назад. [4] — инструменты предыстории."""
    start_level = start_level_for_difficulty(difficulty)
    choices = get_proficiency_choices(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        start_level,
    )
    grants = resolve_creation_grants_with_feats(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        start_level,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
        include_feat_languages=False,
    )
    weapons = list(grants.weapon_tokens)
    armors = list(grants.armor_tokens)
    tools = list(grants.tool_tokens)
    if not choices:
        return weapons, armors, tools, []

    caption = get_string(strings, "character.proficiencies_caption")
    print_screen_header(caption)
    _print_summary(strings, weapons, armors, tools, language)

    background_tool_picks: list[str] = []
    pick_total = sum(c.count for c in choices)
    pick_offset = 0
    for choice in choices:
        picked = _pick_tools(
            strings,
            choice,
            tools,
            language,
            pick_offset + 1,
            pick_total,
        )
        if picked is None:
            return None
        pool = choice.options or []
        if not is_valid_tool_selection(picked, pool, choice.count):
            return None
        tools = merge_unique(tools, picked)
        if choice.source == "background":
            background_tool_picks.extend(picked)
        pick_offset += choice.count

    return weapons, armors, tools, background_tool_picks
