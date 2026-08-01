"""Выбор компетентности (экспертизы) при создании персонажа."""

from colorama import Fore, Style

from core.character.models import Character
from core.mechanics.expertise import (
    ExpertiseGrant,
    default_rogue_tool_expertise,
    get_expertise_grants,
    pending_expertise_grants,
)
from core.platform.localization import get_string
from core.types import StringsDict
from ui.input_handler import get_int_input
from ui.menus.console import (
    pick_n_from_pool_loop,
    print_back_row,
    print_screen_header,
    skill_name,
)


def _pick_expertise_skills(
    strings: StringsDict,
    grant: ExpertiseGrant,
    proficiencies: list[str],
    already_expert: list[str],
    pick_count: int,
) -> list[str] | None:
    """Выбрать навыки для компетентности."""
    taken_suffix = get_string(strings, "character.skills_taken_suffix")
    header = get_string(strings, "character.expertise_caption")
    heading = get_string(
        strings,
        "character.expertise_feature_heading",
        name=grant.feature_name,
    )

    def before_heading(_picked: list[str]) -> None:
        print(f"{Fore.CYAN}{Style.BRIGHT}{heading}{Style.RESET_ALL}")
        print()

    def taken_for_pick(picked: list[str]) -> set[str]:
        return set(already_expert) | set(picked)

    def prompt_at(current: int, total: int) -> str:
        return get_string(
            strings,
            "character.expertise_pick_prompt",
            current=current,
            total=total,
        )

    return pick_n_from_pool_loop(
        strings,
        pick_count,
        pool_for_pick=lambda _picked: list(proficiencies),
        taken_for_pick=taken_for_pick,
        label_for=lambda skill_id: skill_name(strings, skill_id),
        taken_suffix=taken_suffix,
        prompt_at=prompt_at,
        header=header,
        empty_key="character.expertise_pool_empty",
        before_list=before_heading,
    )


def _select_rogue_expertise(
    strings: StringsDict,
    grant: ExpertiseGrant,
    proficiencies: list[str],
) -> tuple[list[str], list[str]] | None:
    """Компетентность плута: 2 навыка или 1 навык + воровские инструменты."""
    while True:
        print_screen_header(get_string(strings, "character.expertise_caption"))
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
        print_back_row(strings)
        print()
        mode = get_int_input(
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


def apply_pending_expertise(
    strings: StringsDict,
    character: Character,
    language: str = "ru",
) -> tuple[list[str], list[str]] | None:
    """Добавить компетентность для grants, ещё не выбранных на персонаже."""
    pending = pending_expertise_grants(character)
    if not pending:
        return list(character.skill_expertise), list(character.tool_expertise)

    all_skill_expertise = list(character.skill_expertise)
    all_tool_expertise = list(character.tool_expertise)

    for grant in pending:
        result = _resolve_grant(strings, grant, character.skills)
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
