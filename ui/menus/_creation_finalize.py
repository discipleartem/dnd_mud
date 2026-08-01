"""Финализация и сохранение персонажа после создания."""

from core.creation_finalize import (
    merge_feat_languages_into,
    persist_built_character,
)
from core.models import Character
from ui.menus._creation_state import _CreationState


def merge_feat_languages(state: _CreationState) -> None:
    """Добавить языки из черт к уже выбранным."""
    state.languages = merge_feat_languages_into(
        state.languages, state.feat_ids, state.feat_choices
    )


def save_created_character(state: _CreationState) -> Character | None:
    """Сохранить персонажа из состояния создания."""
    character = state.to_character()
    if character is None:
        return None
    return persist_built_character(character)
