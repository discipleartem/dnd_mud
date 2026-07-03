"""Финализация и сохранение персонажа после создания."""

from core.character_build import merge_languages_with_feats
from core.character_storage import persist_character
from core.models import Character
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
    character = state.to_character()
    if character is None:
        return None
    return persist_character(character)
