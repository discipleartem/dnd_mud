"""Финализация и сохранение персонажа после создания."""

from core.character_builder import merge_languages_with_feats
from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_success_and_wait
from ui.menus._creation_state import _CreationState


def merge_feat_languages(state: _CreationState) -> None:
    """Добавить языки из черт к уже выбранным."""
    if not state.feat_ids:
        return
    state.languages = merge_languages_with_feats(
        state.languages, state.feat_ids, state.feat_choices
    )


def save_created_character(state: _CreationState) -> Character | None:
    """Сохранить персонажа из состояния создания."""
    kwargs = state.save_kwargs()
    if not kwargs:
        return None
    return _deps.save_character(**kwargs)


def finalize_creation(
    strings: StringsDict, state: _CreationState
) -> Character | None:
    """Сохранить персонажа и показать сообщение об успехе."""
    character = save_created_character(state)
    if character is None:
        return None
    msg = get_string(strings, "character.save_success", name=state.name)
    _print_success_and_wait(strings, msg)
    return character
