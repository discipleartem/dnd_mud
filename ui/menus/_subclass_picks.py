"""Общая логика выбора владений/навыков/экспертизы подкласса."""

from core.models import Character
from core.proficiencies import (
    apply_subclass_proficiencies_to_character,
    is_valid_tool_selection,
    merge_proficiency_tokens,
)
from core.progression.class_features import subclass_skill_picks_pending
from core.types import LanguageCode, StringsDict
from ui.menus.expertise import apply_pending_expertise
from ui.menus.proficiencies import _pick_tools
from ui.menus.skills import add_subclass_skills_from_menu


def apply_subclass_picks(
    strings: StringsDict,
    character: Character,
    subclass_id: str,
    language: LanguageCode,
    *,
    apply_skills: bool | None = None,
) -> Character | None:
    """Выбор инструментов, навыков и экспертизы подкласса. None — отмена."""
    if apply_skills is None:
        apply_skills = subclass_skill_picks_pending(character)

    choices = apply_subclass_proficiencies_to_character(character, subclass_id)
    if choices:
        pick_total = sum(c.count for c in choices)
        pick_offset = 0
        for choice in choices:
            picked = _pick_tools(
                strings,
                choice,
                character.tool_proficiencies,
                language,
                pick_offset + 1,
                pick_total,
            )
            if picked is None:
                return None
            pool = choice.options or []
            if not is_valid_tool_selection(picked, pool, choice.count):
                return None
            character.tool_proficiencies = merge_proficiency_tokens(
                character.tool_proficiencies, picked
            )
            pick_offset += choice.count

    if apply_skills:
        updated_skills = add_subclass_skills_from_menu(
            strings,
            character.class_id,
            subclass_id,
            character.level,
            character.skills,
            language,
        )
        if updated_skills is None:
            return None
        character.skills = updated_skills

    expertise_result = apply_pending_expertise(strings, character, language)
    if expertise_result is None:
        return None
    character.skill_expertise, character.tool_expertise = expertise_result

    return character
