"""Выборные расовые бонусы при генерации характеристик."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.stats import STAT_NAMES
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _ability_name, _choice_prompt


def _select_choice_ability_bonuses(
    strings: dict[str, Any],
    stats: dict[str, int],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Выбор характеристик для выборного расового бонуса."""
    mechanics = _deps.get_choice_ability_bonus_mechanics(race_id, subrace_id)
    if mechanics is None:
        return {}

    count = int(mechanics.get("count", 1))
    value = int(mechanics.get("value", 1))
    allow_duplicates = bool(mechanics.get("allow_duplicates", True))
    chosen_stats: list[str] = []

    for pick_num in range(1, count + 1):
        print(SEPARATOR)
        caption = get_string(strings, "character.stats_choice_bonus_caption")
        print(f"{Fore.YELLOW}{caption.center(78)}{Style.RESET_ALL}")
        print(SEPARATOR)
        print()
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
                print(f"  {_ability_name(strings, stat)} +{value}")
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
            stat_name = _ability_name(strings, stat)
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

        choice = _deps.get_int_input(
            _choice_prompt(strings), 0, len(available), strings
        )
        if choice == 0:
            return None

        chosen_stats.append(available[choice - 1])

    return _deps.build_bonuses_from_choices(chosen_stats, value)


def _finalize_stats_with_race_bonuses(
    strings: dict[str, Any],
    stats: dict[str, int],
    race_id: str,
    subrace_id: str | None,
) -> tuple[dict[str, int], dict[str, int]] | None:
    """Применить выборные бонусы после генерации характеристик."""
    if not _deps.has_choice_ability_bonuses(race_id, subrace_id):
        return stats, _deps.get_race_bonuses(race_id, subrace_id)

    choice_bonuses = _select_choice_ability_bonuses(
        strings, stats, race_id, subrace_id
    )
    if choice_bonuses is None:
        return None

    final_stats = _deps.apply_bonuses_to_stats(stats, choice_bonuses)
    effective_bonuses = _deps.get_effective_race_bonuses(
        race_id, subrace_id, choice_bonuses
    )
    return final_stats, effective_bonuses
