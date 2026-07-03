"""Зависимости UI-меню от core и input_handler.

Единая точка импорта — удобна для monkeypatch в тестах.
Импорты используются как `_deps.<name>` из других модулей пакета.
"""

from core.catalog_loader import reload_catalogs
from core.character import (
    ABILITY_SCORE_DEFAULT,
    ABILITY_SCORE_MAX,
    ABILITY_SCORE_MIN,
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    POINT_BUY_MAX,
    POINT_BUY_MIN,
    STANDARD_ARRAY,
    STANDARD_ARRAY_MAX,
    STANDARD_ARRAY_MIN,
    STAT_NAMES,
    LoadCharactersResult,
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
    get_language_name,
    get_race_bonuses,
    has_choice_ability_bonuses,
    load_adventures,
    load_background_full,
    load_backgrounds,
    load_characters,
    load_class_full,
    load_classes,
    load_languages,
    load_race_full,
    load_races,
    load_strings,
    load_subclasses,
    persist_character,
    point_buy_points_remaining,
    roll_ability_score,
    update_character,
    validate_final_stats,
    validate_point_buy_finish,
)
from core.difficulty import adventure_unavailable_reason
from core.game_engine import GameEngine, GameSession
from core.localization import get_string
from core.mod_loader import set_mod_gating_difficulty
from core.models import Adventure, Character
from core.session_storage import (
    find_adventure,
    list_sessions,
    load_character_for_session,
    load_session,
)
from core.types import (
    GameDifficulty,
    LanguageCode,
    RuntimeSettings,
    StatMap,
    StringsDict,
)
from ui.input_handler import get_int_input, get_str_input


def bootstrap_session_catalogs(difficulty: GameDifficulty) -> None:
    """Синхронизировать mod overlay перед сессией приключения."""
    set_mod_gating_difficulty(difficulty)
    reload_catalogs()


__all__ = [
    "ABILITY_SCORE_DEFAULT",
    "Adventure",
    "ABILITY_SCORE_MAX",
    "ABILITY_SCORE_MIN",
    "Character",
    "GameDifficulty",
    "LanguageCode",
    "POINT_BUY_BUDGET",
    "POINT_BUY_COSTS",
    "POINT_BUY_MAX",
    "POINT_BUY_MIN",
    "STANDARD_ARRAY",
    "STANDARD_ARRAY_MAX",
    "STANDARD_ARRAY_MIN",
    "STAT_NAMES",
    "StatMap",
    "StringsDict",
    "RuntimeSettings",
    "adventure_unavailable_reason",
    "apply_bonuses_to_stats",
    "bootstrap_session_catalogs",
    "build_bonuses_from_choices",
    "can_assign_point_buy_value",
    "delete_all_characters",
    "delete_character",
    "find_adventure",
    "GameEngine",
    "GameSession",
    "generate_stats_point_buy",
    "generate_stats_random",
    "generate_stats_standard_array",
    "get_choice_ability_bonus_mechanics",
    "get_effective_race_bonuses",
    "get_language_name",
    "get_race_bonuses",
    "has_choice_ability_bonuses",
    "get_int_input",
    "get_str_input",
    "get_string",
    "load_adventures",
    "load_background_full",
    "load_backgrounds",
    "load_characters",
    "load_character_for_session",
    "LoadCharactersResult",
    "load_class_full",
    "load_classes",
    "load_languages",
    "load_subclasses",
    "load_race_full",
    "load_races",
    "list_sessions",
    "load_session",
    "load_strings",
    "persist_character",
    "point_buy_points_remaining",
    "roll_ability_score",
    "update_character",
    "validate_final_stats",
    "validate_point_buy_finish",
]
