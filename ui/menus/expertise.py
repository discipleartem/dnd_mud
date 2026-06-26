"""Выбор компетентности (экспертизы) при создании персонажа."""

from colorama import Fore, Style

from core.expertise import (
    ExpertiseGrant,
    default_rogue_tool_expertise,
    get_expertise_grants,
)
from core.localization import get_string
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _skill_name
from ui.menus.skills import _print_skill_pick_list


def _tool_name(strings: StringsDict, tool_id: str) -> str:
    """Локализованное имя инструмента."""
    return get_string(strings, f"tools.{tool_id}")


def _pick_expertise_skills(
    strings: StringsDict,
    grant: ExpertiseGrant,
    proficiencies: list[str],
    already_expert: list[str],
    pick_count: int,
) -> list[str] | None:
    """Выбрать навыки для компетентности."""
    selected: list[str] = []
    for current in range(1, pick_count + 1):
        _print_screen_header(
            get_string(strings, "character.expertise_caption")
        )
        heading = get_string(
            strings,
            "character.expertise_feature_heading",
            name=grant.feature_name,
        )
        print(f"{Fore.CYAN}{Style.BRIGHT}{heading}{Style.RESET_ALL}")
        print()
        prompt = get_string(
            strings,
            "character.expertise_pick_prompt",
            current=current,
            total=pick_count,
        )
        pool = list(proficiencies)
        blocked = list(already_expert) + selected
        selectable = _print_skill_pick_list(strings, pool, blocked)
        print()
        if not selectable:
            print(
                f"{Fore.RED}"
                f"{get_string(strings, 'character.expertise_pool_empty')}"
                f"{Style.RESET_ALL}"
            )
            print()
            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
                f"{get_string(strings, 'character.back')}"
            )
            print()
            if _deps.get_int_input(prompt, 0, 0, strings) == 0:
                return None
            continue

        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.back')}"
        )
        print()
        choice = _deps.get_int_input(prompt, 0, len(selectable), strings)
        if choice == 0:
            return None
        picked = selectable[choice - 1]
        selected.append(picked)

    return selected


def _select_rogue_expertise(
    strings: StringsDict,
    grant: ExpertiseGrant,
    proficiencies: list[str],
) -> tuple[list[str], list[str]] | None:
    """Компетентность плута: 2 навыка или 1 навык + воровские инструменты."""
    while True:
        _print_screen_header(
            get_string(strings, "character.expertise_caption")
        )
        heading = get_string(
            strings,
            "character.expertise_feature_heading",
            name=grant.feature_name,
        )
        print(f"{Fore.CYAN}{Style.BRIGHT}{heading}{Style.RESET_ALL}")
        print()
        print(
            f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.expertise_rogue_mode_skills')}"
        )
        skill_tools_label = get_string(
            strings, "character.expertise_rogue_mode_skill_tools"
        )
        print(f"  {Fore.YELLOW}2{Style.RESET_ALL}. " f"{skill_tools_label}")
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.back')}"
        )
        print()
        mode = _deps.get_int_input(
            get_string(strings, "character.expertise_mode_prompt"),
            0,
            2,
            strings,
        )
        if mode == 0:
            return None
        if mode == 1:
            skills = _pick_expertise_skills(
                strings, grant, proficiencies, [], grant.pick
            )
            if skills is None:
                continue
            return skills, []
        if mode == 2:
            skills = _pick_expertise_skills(
                strings, grant, proficiencies, [], 1
            )
            if skills is None:
                continue
            return skills, default_rogue_tool_expertise()
        continue


def _resolve_grant(
    strings: StringsDict,
    grant: ExpertiseGrant,
    proficiencies: list[str],
) -> tuple[list[str], list[str]] | None:
    """Обработать один grant компетентности."""
    if grant.alternatives:
        return _select_rogue_expertise(strings, grant, proficiencies)

    skills = _pick_expertise_skills(
        strings, grant, proficiencies, [], grant.pick
    )
    if skills is None:
        return None
    return skills, []


def select_creation_expertise(
    strings: StringsDict,
    class_id: str,
    level: int,
    proficiencies: list[str],
    language: str = "ru",
) -> tuple[list[str], list[str]] | None:
    """Выбор компетентности для всех grants на стартовом уровне."""
    grants = get_expertise_grants(class_id, level)
    if not grants:
        return [], []

    all_skill_expertise: list[str] = []
    all_tool_expertise: list[str] = []

    for grant in grants:
        result = _resolve_grant(strings, grant, proficiencies)
        if result is None:
            return None
        skill_part, tool_part = result
        for skill_id in skill_part:
            if skill_id not in all_skill_expertise:
                all_skill_expertise.append(skill_id)
        for tool_id in tool_part:
            if tool_id not in all_tool_expertise:
                all_tool_expertise.append(tool_id)

    return all_skill_expertise, all_tool_expertise


def format_expertise_display(
    strings: StringsDict,
    skill_expertise: list[str],
    tool_expertise: list[str],
) -> str:
    """Строка компетентности для карточки персонажа."""
    parts: list[str] = []
    for skill_id in skill_expertise:
        parts.append(_skill_name(strings, skill_id))
    for tool_id in tool_expertise:
        parts.append(_tool_name(strings, tool_id))
    return ", ".join(parts) if parts else ""
