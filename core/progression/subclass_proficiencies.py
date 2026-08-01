"""Применение владений подкласса к персонажу."""

from core.character.models import Character
from core.mechanics.proficiency_collect import (
    ProficiencyChoice,
    get_subclass_proficiency_tokens,
)
from core.platform.io import merge_unique

__all__ = [
    "apply_picked_tools_to_character",
    "apply_subclass_proficiencies_to_character",
]


def apply_picked_tools_to_character(
    character: Character,
    picked: list[str],
) -> None:
    """Добавить выбранные инструменты к владениям персонажа."""
    character.tool_proficiencies = merge_unique(
        character.tool_proficiencies, picked
    )


def apply_subclass_proficiencies_to_character(
    character: Character,
    subclass_id: str,
) -> list[ProficiencyChoice]:
    """Добавить владения подкласса. Возвращает невыполненные выборы."""
    sw, sa, st, choices = get_subclass_proficiency_tokens(
        character.class_id, subclass_id, character.level
    )
    character.weapon_proficiencies = merge_unique(
        character.weapon_proficiencies, sw
    )
    character.armor_proficiencies = merge_unique(
        character.armor_proficiencies, sa
    )
    character.tool_proficiencies = merge_unique(
        character.tool_proficiencies, st
    )
    return choices
