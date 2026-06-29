"""Flow создания персонажа: раса, предыстория, класс, черты."""

from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header, _print_success_and_wait
from ui.menus._creation_steps import (
    _back_step_from_feats,
    _back_step_from_proficiencies,
    _CreationState,
    _feats_step_required,
    _merge_feat_languages,
    _save_created_character,
    _step_after_class_choice,
    run_creation_steps,
)
from ui.menus._selectors import (
    select_class as _select_class,
)
from ui.menus._selectors import (
    select_subclass as _select_subclass,
)
from ui.menus._selectors import (
    select_subrace as _select_subrace,
)
from ui.menus.backgrounds import select_creation_background
from ui.menus.expertise import select_creation_expertise
from ui.menus.feats import select_creation_feats
from ui.menus.languages import select_creation_languages
from ui.menus.proficiencies import select_creation_proficiencies
from ui.menus.settings import select_difficulty
from ui.menus.skills import select_creation_skills
from ui.menus.stats import show_stats_generation_flow

__all__ = [
    "_CreationState",
    "_back_step_from_feats",
    "_back_step_from_proficiencies",
    "_feats_step_required",
    "_merge_feat_languages",
    "_print_success_and_wait",
    "_save_created_character",
    "_select_class",
    "_select_subclass",
    "_select_subrace",
    "_step_after_class_choice",
    "select_creation_background",
    "select_creation_expertise",
    "select_creation_feats",
    "select_creation_languages",
    "select_creation_proficiencies",
    "select_creation_skills",
    "select_difficulty",
    "show_create_character_flow",
    "show_stats_generation_flow",
]


def show_create_character_flow(
    strings: StringsDict, language: str = "ru"
) -> Character | None:
    """Flow «Создать персонажа»: сложность → создание."""
    difficulty = select_difficulty(strings)
    if difficulty is None:
        return None

    _print_screen_header(get_string(strings, "character.creation_caption"))

    name = _deps.get_str_input(
        get_string(strings, "character.name_prompt"),
        min_length=2,
        only_letters=True,
        strings=strings,
    )

    state = _CreationState(name=name, difficulty=difficulty)
    return run_creation_steps(strings, state, language)
