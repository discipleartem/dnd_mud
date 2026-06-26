"""Оркестратор flow генерации характеристик."""

from core.localization import get_string
from core.types import GameDifficulty, StatMap, StringsDict
from ui.menus._common import (
    _print_screen_header,
    _run_numbered_menu,
)
from ui.menus.stats.stats_methods import (
    _select_stats_point_buy,
    _select_stats_random_hardcore,
    _select_stats_random_normal,
    _select_stats_standard_array,
)


def show_stats_generation_flow(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
    difficulty: GameDifficulty,
    *,
    hardcore_rolls: list[int] | None = None,
) -> StatMap | None:
    """Flow генерации характеристик с выбором метода."""
    if difficulty == "hardcore":
        return _select_stats_random_hardcore(
            strings,
            race_id,
            subrace_id,
            hardcore_rolls=hardcore_rolls,
        )

    while True:
        _print_screen_header(
            get_string(strings, "character.stats_generation_caption")
        )

        methods = [
            get_string(strings, "character.stats_standard_array"),
            get_string(strings, "character.stats_point_buy"),
            get_string(strings, "character.stats_random"),
        ]

        choice = _run_numbered_menu(
            strings,
            methods,
            prompt_key="character.stats_generation_method_prompt",
            back_label_key="character.back",
        )
        if choice is None:
            return None

        if choice == 1:
            stats = _select_stats_standard_array(strings, race_id, subrace_id)
        elif choice == 2:
            stats = _select_stats_point_buy(strings, race_id, subrace_id)
        else:
            stats = _select_stats_random_normal(strings, race_id, subrace_id)

        if stats is not None:
            return stats
