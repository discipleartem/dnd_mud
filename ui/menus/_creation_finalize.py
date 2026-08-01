"""Финализация и сохранение персонажа после создания."""

from core.character.finalize import (
    merge_feat_languages_into,
    persist_built_character,
)
from core.character.models import Character
from core.platform.localization import get_string
from core.types import StringsDict
from ui.menus._creation_state import _CreationState
from ui.menus.console import print_success_and_wait


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


def finalize_creation(
    strings: StringsDict, state: _CreationState
) -> Character | None:
    """Сохранить персонажа и показать сообщение об успехе."""
    character = save_created_character(state)
    if character is None:
        return None
    msg = get_string(strings, "character.save_success", name=state.name)
    print_success_and_wait(strings, msg)
    return character
