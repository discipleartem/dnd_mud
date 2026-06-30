"""Шаги state machine создания персонажа."""

from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import (
    _print_screen_header,
    _print_success_and_wait,
)
from ui.menus._creation_finalize import (
    merge_feat_languages as _merge_feat_languages_impl,
)
from ui.menus._creation_finalize import (
    save_created_character as _save_created_character_impl,
)
from ui.menus._creation_navigation import (
    back_step_from_feats,
    back_step_from_proficiencies,
    back_step_from_skills,
    feats_step_required,
    step_after_class_choice,
)
from ui.menus._creation_state import CreationStep, _CreationState
from ui.menus._selectors import (  # noqa: F401 — monkeypatch seam
    select_class,
    select_subclass,
    select_subrace,
)
from ui.menus.backgrounds import select_creation_background  # noqa: F401
from ui.menus.expertise import select_creation_expertise  # noqa: F401
from ui.menus.feats import select_creation_feats  # noqa: F401
from ui.menus.languages import select_creation_languages  # noqa: F401
from ui.menus.proficiencies import select_creation_proficiencies  # noqa: F401
from ui.menus.settings import select_difficulty
from ui.menus.skills import select_creation_skills  # noqa: F401
from ui.menus.stats.stats_flow import show_stats_generation_flow  # noqa: F401

# Обратная совместимость тестов (monkeypatch на этом модуле)
_feats_step_required = feats_step_required
_step_after_class_choice = step_after_class_choice
_back_step_from_feats = back_step_from_feats
_back_step_from_proficiencies = back_step_from_proficiencies
_back_step_from_skills = back_step_from_skills
_merge_feat_languages = _merge_feat_languages_impl
merge_feat_languages = _merge_feat_languages_impl


def _save_created_character(state: _CreationState) -> Character | None:
    return _save_created_character_impl(state)


def finalize_creation(
    strings: StringsDict, state: _CreationState
) -> Character | None:
    """Сохранить персонажа и показать сообщение об успехе."""
    character = _save_created_character(state)
    if character is None:
        return None
    msg = get_string(strings, "character.save_success", name=state.name)
    _print_success_and_wait(strings, msg)
    return character


_finalize_creation = finalize_creation

__all__ = [
    "CreationStep",
    "_CreationState",
    "_back_step_from_feats",
    "_back_step_from_proficiencies",
    "_back_step_from_skills",
    "_feats_step_required",
    "_finalize_creation",
    "_merge_feat_languages",
    "_save_created_character",
    "_step_after_class_choice",
    "back_step_from_feats",
    "back_step_from_proficiencies",
    "back_step_from_skills",
    "feats_step_required",
    "finalize_creation",
    "merge_feat_languages",
    "run_creation_steps",
    "select_class",
    "select_creation_background",
    "select_creation_expertise",
    "select_creation_feats",
    "select_creation_languages",
    "select_creation_proficiencies",
    "select_creation_skills",
    "select_subclass",
    "select_subrace",
    "show_create_character_flow",
    "show_stats_generation_flow",
    "step_after_class_choice",
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


def run_creation_steps(
    strings: StringsDict,
    state: _CreationState,
    language: str = "ru",
) -> Character | None:
    """Цикл шагов создания персонажа после ввода имени."""
    from ui.menus._creation_handlers import _STEP_HANDLERS

    step: CreationStep = "race"

    while True:
        result = _STEP_HANDLERS[step](strings, state, language)
        if result.character is not None:
            return result.character
        if result.next_step is None:
            return None
        step = result.next_step
