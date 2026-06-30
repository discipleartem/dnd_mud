"""Публичный API экранов меню."""

from ui.menus._creation_steps import show_create_character_flow
from ui.menus.characters_menu import show_characters_menu
from ui.menus.main_menu import (
    show_load_game_flow,
    show_main_menu,
    show_welcome_screen,
)
from ui.menus.new_game import show_new_game_flow
from ui.menus.settings import (
    select_difficulty,
    show_languages_menu,
    show_settings,
)
from ui.menus.stats import show_stats_generation_flow

__all__ = [
    "select_difficulty",
    "show_create_character_flow",
    "show_characters_menu",
    "show_languages_menu",
    "show_load_game_flow",
    "show_main_menu",
    "show_new_game_flow",
    "show_settings",
    "show_stats_generation_flow",
    "show_welcome_screen",
]
