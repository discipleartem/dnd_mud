"""Общие шаги flow генерации характеристик: пул, confirm."""

from typing import Any, Literal

from colorama import Fore, Style

from core.localization import get_string
from ui.menus import _deps
from ui.menus._common import (
    SEPARATOR,
    _ability_name,
    _choice_prompt,
    _stats_total_line,
)
from ui.menus._display import (
    _print_final_stat_line,
    _print_stats_generation_header,
)
from ui.menus.stats.stats_choice_bonuses import (
    _finalize_stats_with_race_bonuses,
)

ConfirmStatsResult = Literal["accept", "reroll", "back"]
StatsConfirmLoopResult = dict[str, int] | None | Literal["reroll"]


def _prompt_pool_value_manual(
    strings: dict[str, Any],
    stat_name: str,
    pool: list[int],
    *,
    value_min: int,
    value_max: int,
) -> int | None:
    """Запросить значение из пула вручную; 0 — назад."""
    display_pool = sorted(pool, reverse=True)
    enter_msg = get_string(
        strings, "character.stats_enter_value_for", stat=stat_name
    )
    back_hint = get_string(strings, "character.stats_enter_value_back_hint")

    while True:
        print(f"{Fore.YELLOW}{enter_msg} {back_hint}{Style.RESET_ALL}")
        print()
        value = _deps.get_int_input(
            _choice_prompt(strings), 0, value_max, strings
        )
        if value == 0:
            return None
        if value < value_min:
            err = get_string(
                strings,
                "character.stats_value_not_in_pool",
                value=value,
                values=display_pool,
            )
            print(f"{Fore.RED}{err}{Style.RESET_ALL}")
            continue
        if value in pool:
            return value
        err = get_string(
            strings,
            "character.stats_value_not_in_pool",
            value=value,
            values=display_pool,
        )
        print(f"{Fore.RED}{err}{Style.RESET_ALL}")


def _prompt_point_buy_stat_value(
    strings: dict[str, Any],
    stat_name: str,
    stats: dict[str, int],
    stat: str,
) -> None:
    """Запросить новое значение point-buy для характеристики."""
    enter_msg = get_string(
        strings, "character.stats_enter_point_buy_value", stat=stat_name
    )

    while True:
        print(f"{Fore.YELLOW}{enter_msg}{Style.RESET_ALL}")
        print()
        value = _deps.get_int_input(
            _choice_prompt(strings),
            _deps.POINT_BUY_MIN,
            _deps.POINT_BUY_MAX,
            strings,
        )
        if _deps.can_assign_point_buy_value(stats, stat, value):
            stats[stat] = value
            return
        if value not in _deps.POINT_BUY_COSTS:
            print(
                f"{Fore.RED}"
                f"{get_string(strings, 'character.stats_max_value_15')}"
                f"{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.RED}"
                f"{get_string(strings, 'character.stats_not_enough_points')}"
                f"{Style.RESET_ALL}"
            )


def _assign_stats_from_pool(
    strings: dict[str, Any],
    available: list[int],
    *,
    value_min: int,
    value_max: int,
    show_counts: bool = False,
    race_id: str | None = None,
    subrace_id: str | None = None,
) -> dict[str, int] | None:
    """Распределить значения из пула по характеристикам."""
    selected: dict[str, int] = {}
    pool = list(available)

    for stat in _deps.STAT_NAMES:
        stat_name = _ability_name(strings, stat)
        _print_stats_generation_header(strings, race_id, subrace_id)

        if selected:
            print(
                f"{Fore.GREEN}"
                f"{get_string(strings, 'character.stats_selected_label')}"
                f"{Style.RESET_ALL}"
            )
            for s, v in selected.items():
                s_name = _ability_name(strings, s)
                print(f"  {s_name}: {v}")
            print()

        display_values = pool if show_counts else sorted(pool, reverse=True)
        avail_msg = get_string(
            strings,
            "character.stats_available",
            values=display_values,
        )
        print(f"{Fore.CYAN}{avail_msg}{Style.RESET_ALL}")
        print()

        selected_value = _prompt_pool_value_manual(
            strings,
            stat_name,
            pool,
            value_min=value_min,
            value_max=value_max,
        )
        if selected_value is None:
            return None

        selected[stat] = selected_value
        pool.remove(selected_value)

    return selected


def _confirm_stats(
    strings: dict[str, Any],
    stats: dict[str, int],
    race_id: str,
    subrace_id: str | None,
    *,
    reroll_label_key: str,
    race_bonuses: dict[str, int] | None = None,
) -> ConfirmStatsResult:
    """Подтверждение выбранных характеристик."""
    if race_bonuses is None:
        race_bonuses = _deps.get_race_bonuses(race_id, subrace_id)

    print(SEPARATOR)
    print(_stats_total_line(strings))
    print(SEPARATOR)
    print()

    for stat in _deps.STAT_NAMES:
        _print_final_stat_line(
            strings, stat, stats.get(stat, 10), race_bonuses
        )

    print()
    print(
        f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
        f"{get_string(strings, 'character.stats_confirm')}"
    )
    print(
        f"  {Fore.YELLOW}2{Style.RESET_ALL}. "
        f"{get_string(strings, reroll_label_key)}"
    )
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()

    choice = _deps.get_int_input(_choice_prompt(strings), 0, 2, strings)

    if choice == 0:
        return "back"
    if choice == 2:
        return "reroll"
    return "accept"


def _run_stats_confirm_loop(
    strings: dict[str, Any],
    stats: dict[str, int],
    race_id: str,
    subrace_id: str | None,
    reroll_label_key: str,
) -> StatsConfirmLoopResult:
    """Подтверждение характеристик: accept → stats, back → None, reroll."""
    finalized = _finalize_stats_with_race_bonuses(
        strings, stats, race_id, subrace_id
    )
    if finalized is None:
        return "reroll"
    final_stats, race_bonuses = finalized
    result = _confirm_stats(
        strings,
        final_stats,
        race_id,
        subrace_id,
        reroll_label_key=reroll_label_key,
        race_bonuses=race_bonuses,
    )
    if result == "accept":
        return final_stats
    if result == "back":
        return None
    return "reroll"
