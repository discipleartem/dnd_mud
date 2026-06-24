"""Методы генерации характеристик: standard array, point-buy, random."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from ui.menus import _common, _deps
from ui.menus._common import _ability_name, _choice_prompt
from ui.menus._display import (
    _print_point_buy_cost_table,
    _print_stats_generation_header,
)
from ui.menus.stats.stats_choice_bonuses import (
    _finalize_stats_with_race_bonuses,
)
from ui.menus.stats.stats_shared import (
    _assign_stats_from_pool,
    _confirm_stats,
    _prompt_point_buy_stat_value,
    _run_stats_confirm_loop,
)


def _select_stats_standard_array(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Выбор характеристик из стандартного массива."""
    while True:
        selected = _assign_stats_from_pool(
            strings,
            list(_deps.STANDARD_ARRAY),
            value_min=_deps.STANDARD_ARRAY_MIN,
            value_max=_deps.STANDARD_ARRAY_MAX,
            race_id=race_id,
            subrace_id=subrace_id,
        )
        if selected is None:
            return None

        selected_values = [selected[stat] for stat in _deps.STAT_NAMES]
        stats = _deps.generate_stats_standard_array(
            selected_values, race_id, subrace_id
        )
        result = _run_stats_confirm_loop(
            strings,
            stats,
            race_id,
            subrace_id,
            reroll_label_key="character.stats_reroll_redistribute",
        )
        if result == "reroll":
            continue
        return result


def _select_stats_point_buy(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Система покупки очков (Point-buy)."""
    while True:
        stats = {stat: 8 for stat in _deps.STAT_NAMES}

        while True:
            _print_stats_generation_header(strings, race_id, subrace_id)
            _print_point_buy_cost_table(strings)

            stat_values = [stats[stat] for stat in _deps.STAT_NAMES]
            points_available = _deps.point_buy_points_remaining(stat_values)

            points_msg = get_string(
                strings,
                "character.stats_points_available",
                available=points_available,
                total=_deps.POINT_BUY_BUDGET,
            )
            print(f"{Fore.CYAN}{points_msg}{Style.RESET_ALL}")
            print()
            print(
                f"{Fore.YELLOW}"
                f"{get_string(strings, 'character.stats_current')}"
                f"{Style.RESET_ALL}"
            )

            for idx, stat in enumerate(_deps.STAT_NAMES, 1):
                stat_name = _ability_name(strings, stat)
                cost = _deps.POINT_BUY_COSTS[stats[stat]]
                cost_msg = get_string(
                    strings, "character.stats_cost_points", cost=cost
                )
                print(
                    f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {stat_name}: "
                    f"{Fore.CYAN}{stats[stat]}{Style.RESET_ALL} {cost_msg}"
                )

            print()
            print(
                f"{Fore.GREEN}"
                f"{get_string(strings, 'character.stats_commands')}"
                f"{Style.RESET_ALL}"
            )
            choose_increase = get_string(
                strings, "character.stats_choose_stat_increase"
            )
            print(
                f"  {Fore.YELLOW}1-6{Style.RESET_ALL}. " f"{choose_increase}"
            )
            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
                f"{get_string(strings, 'character.stats_finish_distribution')}"
            )
            print()

            choice = _deps.get_int_input(
                _choice_prompt(strings), 0, 6, strings
            )

            if choice == 0:
                error_key = _deps.validate_point_buy_finish(stat_values)
                if error_key is None:
                    stats_result = _deps.generate_stats_point_buy(
                        stat_values, race_id, subrace_id
                    )
                    result = _run_stats_confirm_loop(
                        strings,
                        stats_result,
                        race_id,
                        subrace_id,
                        reroll_label_key="character.stats_reroll_redistribute",
                    )
                    if result == "reroll":
                        break
                    return result
                if error_key == "character.stats_points_unspent":
                    unspent = get_string(
                        strings,
                        error_key,
                        remaining=points_available,
                    )
                    print(f"{Fore.RED}{unspent}{Style.RESET_ALL}")
                else:
                    overspent = get_string(strings, error_key)
                    print(f"{Fore.RED}{overspent}{Style.RESET_ALL}")
                _common._press_enter(strings)
                continue

            stat_to_modify = _deps.STAT_NAMES[choice - 1]
            stat_name = _ability_name(strings, stat_to_modify)
            _prompt_point_buy_stat_value(
                strings, stat_name, stats, stat_to_modify
            )


def _select_stats_random_normal(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Случайный метод для Normal режима с распределением значений."""
    rolls: list[int] | None = None

    while True:
        _print_stats_generation_header(strings, race_id, subrace_id)

        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.stats_generating_random')}"
            f"{Style.RESET_ALL}"
        )
        print()

        if rolls is None:
            rolls = [_deps.roll_ability_score() for _ in range(6)]
            rolls.sort(reverse=True)

        print(
            f"{Fore.CYAN}"
            f"{get_string(strings, 'character.stats_random_rolls')}"
            f"{Style.RESET_ALL}"
        )
        rolls_display = get_string(
            strings,
            "character.stats_available",
            values=rolls,
        )
        print(f"  {rolls_display}")
        print()
        print(
            f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.stats_random_accept')}"
        )
        print(
            f"  {Fore.YELLOW}2{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.stats_random_regenerate')}"
        )
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}. "
            f"{get_string(strings, 'character.back')}"
        )
        print()

        roll_choice = _deps.get_int_input(
            _choice_prompt(strings), 0, 2, strings
        )
        if roll_choice == 0:
            return None
        if roll_choice == 2:
            rolls = None
            continue

        while True:
            selected = _assign_stats_from_pool(
                strings,
                rolls,
                value_min=min(rolls),
                value_max=max(rolls),
                show_counts=True,
                race_id=race_id,
                subrace_id=subrace_id,
            )
            if selected is None:
                break

            selected_values = [selected[stat] for stat in _deps.STAT_NAMES]
            stats = _deps.generate_stats_random(
                selected_values, race_id, subrace_id
            )
            result = _run_stats_confirm_loop(
                strings,
                stats,
                race_id,
                subrace_id,
                reroll_label_key="character.stats_reroll_regenerate",
            )
            if result == "reroll":
                rolls = None
                break
            return result


def _select_stats_random_hardcore(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int]:
    """Случайный метод для HardCore режима."""
    base_values = [_deps.roll_ability_score() for _ in _deps.STAT_NAMES]

    while True:
        _print_stats_generation_header(strings, race_id, subrace_id)
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.stats_hardcore_auto')}"
            f"{Style.RESET_ALL}"
        )
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'character.stats_hardcore_method')}"
            f"{Style.RESET_ALL}"
        )
        print()

        for stat, roll in zip(_deps.STAT_NAMES, base_values, strict=True):
            stat_name = _ability_name(strings, stat)
            print(f"  {stat_name}: {Fore.YELLOW}{roll}{Style.RESET_ALL}")

        print()
        _common._press_enter(strings)

        stats = _deps.generate_stats_random(base_values, race_id, subrace_id)
        finalized = _finalize_stats_with_race_bonuses(
            strings, stats, race_id, subrace_id
        )
        if finalized is None:
            continue
        final_stats, race_bonuses = finalized

        result = _confirm_stats(
            strings,
            final_stats,
            race_id,
            subrace_id,
            reroll_label_key="character.stats_reroll_regenerate",
            race_bonuses=race_bonuses,
        )
        if result == "accept":
            return final_stats
        if result == "back":
            continue
        base_values = [_deps.roll_ability_score() for _ in _deps.STAT_NAMES]
