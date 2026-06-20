"""Оркестратор flow генерации характеристик."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _stats_caption_line
from ui.menus.stats.stats_methods import (
    _select_stats_point_buy,
    _select_stats_random_hardcore,
    _select_stats_random_normal,
    _select_stats_standard_array,
)


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
