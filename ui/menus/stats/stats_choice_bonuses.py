"""Выборные расовые бонусы при генерации характеристик."""

from colorama import Fore, Style

from core.catalogs.races import (
    build_bonuses_from_choices,
    get_choice_ability_bonus_mechanics,
    get_effective_race_bonuses,
    get_race_bonuses,
    has_choice_ability_bonuses,
)
from core.mechanics.stats import STAT_NAMES, apply_bonuses_to_stats
from core.platform.localization import get_string
from core.types import StatMap, StringsDict
from ui.input_handler import get_int_input
from ui.menus.console import (
    ability_name,
    choice_prompt,
    print_screen_header,
)


def _select_choice_ability_bonuses(
    strings: StringsDict,
    stats: StatMap,
    race_id: str,
    subrace_id: str | None,
) -> StatMap | None:
    """Выбор характеристик для выборного расового бонуса."""
    mechanics = get_choice_ability_bonus_mechanics(race_id, subrace_id)
    if mechanics is None:
        return {}

    count = int(mechanics.get("count", 1))
    value = int(mechanics.get("amount", 1))
    allow_duplicates = bool(mechanics.get("allow_duplicates", True))
    chosen_stats: list[str] = []

    for pick_num in range(1, count + 1):
        print_screen_header(
            get_string(strings, "character.stats_choice_bonus_caption")
        )
        prompt = get_string(
            strings,
            "character.stats_choice_bonus_prompt",
            current=pick_num,
            total=count,
            value=value,
        )
        print(f"{Fore.CYAN}{prompt}{Style.RESET_ALL}")
        print()

        if chosen_stats:
            print(
                f"{Fore.GREEN}"
                f"{get_string(strings, 'character.stats_selected_label')}"
                f"{Style.RESET_ALL}"
            )
            for stat in chosen_stats:
                print(f"  {ability_name(strings, stat)} +{value}")
            print()

        available = list(STAT_NAMES)
        if not allow_duplicates:
            available = [s for s in STAT_NAMES if s not in chosen_stats]

        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.stats_current')}"
            f"{Style.RESET_ALL}"
        )
        for idx, stat in enumerate(available, 1):
            stat_name = ability_name(strings, stat)
            stat_msg = get_string(
                strings,
                "character.stat_line",
                stat=stat_name,
                value=stats[stat],
            )
            print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {stat_msg}")

        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()

        choice = get_int_input(
            choice_prompt(strings), 0, len(available), strings
        )
        if choice == 0:
            return None

        chosen_stats.append(available[choice - 1])

    return build_bonuses_from_choices(chosen_stats, value)


def _finalize_stats_with_race_bonuses(
    strings: StringsDict,
    stats: StatMap,
    race_id: str,
    subrace_id: str | None,
) -> tuple[StatMap, StatMap] | None:
    """Применить выборные бонусы после генерации характеристик."""
    if not has_choice_ability_bonuses(race_id, subrace_id):
        return stats, get_race_bonuses(race_id, subrace_id)

    choice_bonuses = _select_choice_ability_bonuses(
        strings, stats, race_id, subrace_id
    )
    if choice_bonuses is None:
        return None

    final_stats = apply_bonuses_to_stats(stats, choice_bonuses)
    effective_bonuses = get_effective_race_bonuses(
        race_id, subrace_id, choice_bonuses
    )
    return final_stats, effective_bonuses
