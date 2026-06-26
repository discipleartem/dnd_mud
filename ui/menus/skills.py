"""Выбор навыков при создании персонажа."""

from colorama import Fore, Style

from core.localization import get_string
from core.skills import (
    get_class_skill_config,
    get_fixed_racial_proficiencies_with_source,
    get_race_skill_choices_with_source,
    resolve_skill_pool,
)
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _skill_name

SkillSource = str


def _source_label(strings: StringsDict, source: SkillSource) -> str:
    """Локализованная подпись источника владения."""
    return get_string(strings, f"character.skills_source_{source}")


def _print_proficient_summary(
    strings: StringsDict,
    proficient: list[str],
    sources: dict[str, SkillSource],
) -> None:
    """Показать уже выбранные навыки с указанием источника."""
    if not proficient:
        return
    print(
        f"{Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'character.skills_proficient_heading')}"
        f"{Style.RESET_ALL}"
    )
    for skill_id in proficient:
        name = _skill_name(strings, skill_id)
        source = _source_label(strings, sources[skill_id])
        line = get_string(
            strings,
            "character.skills_proficient_line",
            skill=name,
            source=source,
        )
        print(f"  {Fore.CYAN}{line}{Style.RESET_ALL}")
    print()


def _print_skill_pick_list(
    strings: StringsDict,
    pool: list[str],
    proficient_so_far: list[str],
) -> list[str]:
    """Показать пул навыков; занятые — серым. Вернуть доступные для выбора."""
    taken_suffix = get_string(strings, "character.skills_taken_suffix")
    selectable: list[str] = []
    for skill_id in pool:
        name = _skill_name(strings, skill_id)
        if skill_id in proficient_so_far:
            print(
                f"  {Fore.LIGHTBLACK_EX}{name} {taken_suffix}"
                f"{Style.RESET_ALL}"
            )
        else:
            selectable.append(skill_id)
            idx = len(selectable)
            print(
                f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
                f"{Fore.CYAN}{name}{Style.RESET_ALL}"
            )
    return selectable


def _pick_one_skill(
    strings: StringsDict,
    pool: list[str],
    proficient: list[str],
    sources: dict[str, SkillSource],
    prompt_key: str,
    current: int,
    total: int,
) -> str | None:
    """Выбрать один навык из пула или вернуть None при «Назад»."""
    while True:
        _print_screen_header(get_string(strings, "character.skills_caption"))
        _print_proficient_summary(strings, proficient, sources)
        prompt = get_string(
            strings,
            prompt_key,
            current=current,
            total=total,
        )
        selectable = _print_skill_pick_list(strings, pool, proficient)
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
            choice = _deps.get_int_input(prompt, 0, 0, strings)
            if choice == 0:
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
        return selectable[choice - 1]


def _add_proficiency(
    proficient: list[str],
    sources: dict[str, SkillSource],
    skill_id: str,
    source: SkillSource,
) -> None:
    """Добавить владение, если его ещё нет."""
    if skill_id not in proficient:
        proficient.append(skill_id)
        sources[skill_id] = source


def select_creation_skills(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    language: str = "ru",
) -> list[str] | None:
    """Выбор навыков: классовые, затем расовые выборные; раса — сразу."""
    proficient: list[str] = []
    sources: dict[str, SkillSource] = {}

    for skill_id, source in get_fixed_racial_proficiencies_with_source(
        race_id, subrace_id
    ):
        _add_proficiency(proficient, sources, skill_id, source)

    class_pool, class_count = get_class_skill_config(class_id)
    for pick_idx in range(1, class_count + 1):
        picked = _pick_one_skill(
            strings,
            class_pool,
            proficient,
            sources,
            "character.skills_class_pick_prompt",
            pick_idx,
            class_count,
        )
        if picked is None:
            return None
        _add_proficiency(proficient, sources, picked, "class")

    racial_choices = get_race_skill_choices_with_source(race_id, subrace_id)
    racial_pick_total = sum(
        int(mechanics.get("count", 0)) for mechanics, _source in racial_choices
    )
    racial_current = 0
    for mechanics, choice_source in racial_choices:
        count = int(mechanics.get("count", 0))
        from_list = str(mechanics.get("from_list", "all"))
        pool = resolve_skill_pool(from_list, class_id)
        for _ in range(count):
            racial_current += 1
            picked = _pick_one_skill(
                strings,
                pool,
                proficient,
                sources,
                "character.skills_racial_pick_prompt",
                racial_current,
                racial_pick_total,
            )
            if picked is None:
                return None
            _add_proficiency(proficient, sources, picked, choice_source)

    return proficient
