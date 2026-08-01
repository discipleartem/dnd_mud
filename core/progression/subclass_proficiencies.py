"""Применение владений подкласса к персонажу."""

from core.character.models import Character
from core.mechanics.proficiency_collect import (
    ProficiencyChoice,
    get_subclass_proficiency_tokens,
    merge_proficiency_tokens,
)

__all__ = ["apply_subclass_proficiencies_to_character"]


def apply_subclass_proficiencies_to_character(
    character: Character,
    subclass_id: str,
) -> list[ProficiencyChoice]:
    """Добавить владения подкласса. Возвращает невыполненные выборы."""
    sw, sa, st, choices = get_subclass_proficiency_tokens(
        character.class_id, subclass_id, character.level
    )
    character.weapon_proficiencies = merge_proficiency_tokens(
        character.weapon_proficiencies, sw
    )
    character.armor_proficiencies = merge_proficiency_tokens(
        character.armor_proficiencies, sa
    )
    character.tool_proficiencies = merge_proficiency_tokens(
        character.tool_proficiencies, st
    )
    return choices
