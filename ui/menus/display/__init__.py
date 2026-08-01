"""Публичный API отображения меню."""

from core.inventory.equipped_display import (
    format_versatile_damage_dice,
    get_equipped_display,
)
from ui.menus.display.character_card import (
    _format_character_feats,
    _print_character_card,
    _print_characters_list,
)
from ui.menus.display.class_info import (
    _format_class_proficiencies,
    _print_class_info,
    _print_class_summary,
    _print_subclass_info,
)
from ui.menus.display.equipment_view import format_inventory_line
from ui.menus.display.grants import (
    format_grant_line_text,
)
from ui.menus.display.race_background import (
    _format_bonuses,
    _print_background_info,
    _print_race_bonuses,
    _print_race_info,
)
from ui.menus.display.stats import (
    _format_ability_modifier,
    _format_character_stats_compact,
    _print_final_stat_line,
    _print_point_buy_cost_table,
    _print_stats_generation_header,
)

__all__ = [
    "_format_ability_modifier",
    "_format_bonuses",
    "_format_character_feats",
    "_format_character_stats_compact",
    "_format_class_proficiencies",
    "_print_background_info",
    "_print_character_card",
    "_print_characters_list",
    "_print_class_info",
    "_print_class_summary",
    "_print_final_stat_line",
    "_print_point_buy_cost_table",
    "_print_race_bonuses",
    "_print_race_info",
    "_print_stats_generation_header",
    "_print_subclass_info",
    "format_grant_line_text",
    "format_inventory_line",
    "format_versatile_damage_dice",
    "get_equipped_display",
]
