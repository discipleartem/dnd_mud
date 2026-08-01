"""Финализация создания персонажа без UI-состояния."""

from typing import Any

from core.character_storage import persist_character
from core.grants_resolve import merge_languages_with_feats
from core.models import Character


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
