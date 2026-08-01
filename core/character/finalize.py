"""Финализация создания персонажа без UI-состояния."""

from typing import Any

from core.character.models import Character
from core.character.storage import persist_character
from core.grants.resolve import merge_languages_with_feats


def merge_feat_languages_into(
    languages: list[str] | None,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None,
) -> list[str]:
    """Языки после слияния с выборами черт."""
    if not feat_ids:
        return list(languages) if languages else []
    return merge_languages_with_feats(languages, feat_ids, feat_choices)


def persist_built_character(character: Character) -> Character:
    """Записать собранного персонажа на диск."""
    return persist_character(character)
