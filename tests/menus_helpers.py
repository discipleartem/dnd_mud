"""Re-export приватных функций меню для тестов."""

from ui.menus.character_flow import _select_class, _select_subrace
from ui.menus.new_game import _select_adventure, _select_character
from ui.menus.stats import (
    _assign_stats_from_pool,
    _confirm_stats,
    _prompt_point_buy_stat_value,
    _prompt_pool_value_manual,
    _select_stats_point_buy,
    _select_stats_random_hardcore,
    _select_stats_standard_array,
)

__all__ = [
    "_assign_stats_from_pool",
    "_confirm_stats",
    "_prompt_point_buy_stat_value",
    "_prompt_pool_value_manual",
    "_select_adventure",
    "_select_character",
    "_select_class",
    "_select_stats_point_buy",
    "_select_stats_random_hardcore",
    "_select_stats_standard_array",
    "_select_subrace",
]
