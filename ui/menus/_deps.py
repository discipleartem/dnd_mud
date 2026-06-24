"""Зависимости UI-меню от core и input_handler.

Единая точка импорта — удобна для monkeypatch в тестах.
Импорты используются как `_deps.<name>` из других модулей пакета.
"""

from core.adventure import load_adventures
from core.character import (
    apply_bonuses_to_stats,
    build_bonuses_from_choices,
    can_assign_point_buy_value,
    delete_all_characters,
    delete_character,
    generate_stats_point_buy,
    generate_stats_random,
    generate_stats_standard_array,
    get_choice_ability_bonus_mechanics,
    get_effective_race_bonuses,
    get_race_bonuses,
    has_choice_ability_bonuses,
    load_characters,
    load_classes,
    load_race_full,
    load_races,
    point_buy_points_remaining,
    save_character,
    validate_point_buy_finish,
)
from core.dice import roll_ability_score
from core.localization import load_strings
from core.stats import (
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    POINT_BUY_MAX,
    POINT_BUY_MIN,
    STANDARD_ARRAY,
    STANDARD_ARRAY_MAX,
    STANDARD_ARRAY_MIN,
    STAT_NAMES,
)
from ui.input_handler import get_int_input, get_str_input

__all__ = [
    "POINT_BUY_BUDGET",
    "POINT_BUY_COSTS",
    "POINT_BUY_MAX",
    "POINT_BUY_MIN",
    "STANDARD_ARRAY",
    "STANDARD_ARRAY_MAX",
    "STANDARD_ARRAY_MIN",
    "STAT_NAMES",
    "apply_bonuses_to_stats",
    "build_bonuses_from_choices",
    "can_assign_point_buy_value",
    "delete_all_characters",
    "delete_character",
    "generate_stats_point_buy",
    "generate_stats_random",
    "generate_stats_standard_array",
    "get_choice_ability_bonus_mechanics",
    "get_effective_race_bonuses",
    "get_race_bonuses",
    "has_choice_ability_bonuses",
    "get_int_input",
    "get_str_input",
    "load_adventures",
    "load_characters",
    "load_classes",
    "load_race_full",
    "load_races",
    "load_strings",
    "point_buy_points_remaining",
    "roll_ability_score",
    "save_character",
    "validate_point_buy_finish",
]
