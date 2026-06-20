"""Flow генерации характеристик персонажа."""

from typing import Any, Literal

from colorama import Fore, Style

from core.localization import get_string
from ui.menus import _common, _deps
from ui.menus._common import (
    SEPARATOR,
    _ability_name,
    _choice_prompt,
    _stats_caption_line,
    _stats_total_line,
)
from ui.menus._display import (
    _print_final_stat_line,
    _print_point_buy_cost_table,
    _print_stats_generation_header,
)

ConfirmStatsResult = Literal["accept", "reroll", "back"]
StatsConfirmLoopResult = dict[str, int] | None | Literal["reroll"]

STAT_NAMES = _deps.STAT_NAMES
STANDARD_ARRAY = _deps.STANDARD_ARRAY
STANDARD_ARRAY_MIN = _deps.STANDARD_ARRAY_MIN
STANDARD_ARRAY_MAX = _deps.STANDARD_ARRAY_MAX
POINT_BUY_BUDGET = _deps.POINT_BUY_BUDGET
POINT_BUY_COSTS = _deps.POINT_BUY_COSTS
POINT_BUY_MIN = _deps.POINT_BUY_MIN
POINT_BUY_MAX = _deps.POINT_BUY_MAX


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
            _choice_prompt(strings), POINT_BUY_MIN, POINT_BUY_MAX, strings
        )
        if _deps.can_assign_point_buy_value(stats, stat, value):
            stats[stat] = value
            return
        if value not in POINT_BUY_COSTS:
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

    for stat in STAT_NAMES:
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

    for stat in STAT_NAMES:
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


def show_stats_generation_flow(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
    difficulty: str,
) -> dict[str, int] | None:
    """Flow генерации характеристик с выбором метода."""
    if difficulty == "hardcore":
        return _select_stats_random_hardcore(strings, race_id, subrace_id)

    while True:
        print(SEPARATOR)
        print(_stats_caption_line(strings))
        print(SEPARATOR)
        print()

        methods = [
            get_string(strings, "character.stats_standard_array"),
            get_string(strings, "character.stats_point_buy"),
            get_string(strings, "character.stats_random"),
        ]

        for idx, method in enumerate(methods, 1):
            print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {method}")
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()

        choice = _deps.get_int_input(
            get_string(strings, "character.stats_generation_method_prompt"),
            0,
            3,
            strings,
        )

        if choice == 0:
            return None

        stats: dict[str, int] | None = None
        if choice == 1:
            stats = _select_stats_standard_array(strings, race_id, subrace_id)
        elif choice == 2:
            stats = _select_stats_point_buy(strings, race_id, subrace_id)
        elif choice == 3:
            stats = _select_stats_random_normal(strings, race_id, subrace_id)

        if stats is not None:
            return stats


def _select_stats_standard_array(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
) -> dict[str, int] | None:
    """Выбор характеристик из стандартного массива."""
    while True:
        selected = _assign_stats_from_pool(
            strings,
            list(STANDARD_ARRAY),
            value_min=STANDARD_ARRAY_MIN,
            value_max=STANDARD_ARRAY_MAX,
            race_id=race_id,
            subrace_id=subrace_id,
        )
        if selected is None:
            return None

        selected_values = [selected[stat] for stat in STAT_NAMES]
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
        stats = {stat: 8 for stat in STAT_NAMES}

        while True:
            _print_stats_generation_header(strings, race_id, subrace_id)
            _print_point_buy_cost_table(strings)

            stat_values = [stats[stat] for stat in STAT_NAMES]
            points_available = _deps.point_buy_points_remaining(stat_values)

            points_msg = get_string(
                strings,
                "character.stats_points_available",
                available=points_available,
                total=POINT_BUY_BUDGET,
            )
            print(f"{Fore.CYAN}{points_msg}{Style.RESET_ALL}")
            print()
            print(
                f"{Fore.YELLOW}"
                f"{get_string(strings, 'character.stats_current')}"
                f"{Style.RESET_ALL}"
            )

            for idx, stat in enumerate(STAT_NAMES, 1):
                stat_name = _ability_name(strings, stat)
                cost = POINT_BUY_COSTS[stats[stat]]
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

            stat_to_modify = STAT_NAMES[choice - 1]
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

            selected_values = [selected[stat] for stat in STAT_NAMES]
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
    base_values = [_deps.roll_ability_score() for _ in STAT_NAMES]

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

        for stat, roll in zip(STAT_NAMES, base_values, strict=True):
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

        print(SEPARATOR)
        print(_stats_total_line(strings))
        print(SEPARATOR)
        print()

        for stat in STAT_NAMES:
            _print_final_stat_line(
                strings, stat, final_stats[stat], race_bonuses
            )

        print()
        _common._press_enter(strings)

        return final_stats
